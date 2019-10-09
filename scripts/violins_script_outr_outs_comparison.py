import os
from typing import Generator, List

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

SAMPLES = ['Pre-Tx', 'Week4']
POP_01 = 'non-outliers'  # 'top outliers', 'bottom outliers', 'non-outliers', 'whole population', 'none'
POP_02 = 'top outliers'  # 'top outliers', 'bottom outliers', 'non-outliers', 'whole population', 'none'
MARKER = '(Gd156)Di<CXCR3-156>'
REFERENCE = True
GATE = False
BASE_PATH = '/home/juliano/Repositories/my-github-repositories/SCOUTS/local/sample data/MP29_CD45low'
SCOUTS_PATH = os.path.join(BASE_PATH, 'scouts output')
COLORS = {
    'top outliers': [0.988, 0.553, 0.384],     # green
    'bottom outliers': [0.259, 0.455, 0.643],  # blue
    'non-outliers': [0.400, 0.761, 0.647],     # orange
    'whole population': [0.600, 0.600, 0.600]  # gray
}


def plot(samples: List[str], pop_01: str, pop_02: str, marker: str, reference: bool, population_df: pd.DataFrame,
         summary_df: pd.DataFrame, scouts_path: str) -> None:
    pops_to_analyse = [pop_01, pop_02]
    columns = ['sample', 'marker', 'population', 'expression']
    violins_df = pd.DataFrame(columns=columns, dtype=float)
    for pop in pops_to_analyse:
        if pop == 'whole population':
            for partial_df in yield_violin_values(df=population_df, population='whole population', samples=samples,
                                                  marker=marker, columns=columns):
                violins_df = violins_df.append(partial_df)
        elif pop != 'none':
            for file_number in yield_selected_file_numbers(summary_df=summary_df, population=pop, reference=reference,
                                                           marker=marker):
                df_path = os.path.join(scouts_path, 'data', f'{"%04d" % file_number}.')
                try:
                    sample_df = pd.read_excel(df_path + 'xlsx', index_col=0)
                except FileNotFoundError:
                    sample_df = pd.read_csv(df_path + 'csv', index_col=0)
                if not sample_df.empty:
                    for partial_df in yield_violin_values(df=sample_df, population=pop, samples=samples, marker=marker,
                                                          columns=columns):
                        violins_df = violins_df.append(partial_df)
    pops_to_analyse = [p for p in pops_to_analyse if p != 'none']
    palette = [COLORS[pop] for pop in pops_to_analyse]
    violins_df.loc[:, 'expression'] = np.log(violins_df.loc[:, 'expression'])
    fig, ax = plt.subplots()
    sns.violinplot(ax=ax, data=violins_df, x='sample', y='expression', order=samples, scale='width', hue='population',
                   dodge=False, color='white', palette=palette)
    ax.set_xlim(-0.5, len(samples) - 0.5)
    ref_str = 'OutR' if reference else 'OutS'
    ax.set_title(f'{marker} expression - {ref_str}')
    plt.show()


def yield_violin_values(df: pd.DataFrame, population: str, samples: List[str], marker: str,
                        columns: List[str]) -> pd.DataFrame:
    for sample in samples:
        series = df.loc[df.index.str.contains(sample)].loc[:, marker]
        yield pd.DataFrame({'sample': sample, 'marker': marker, 'population': population, 'expression': series},
                           columns=columns)


def yield_selected_file_numbers(summary_df: pd.DataFrame, population: str, reference: bool,
                                marker: str) -> Generator[pd.DataFrame, None, None]:
    cutoff = 'reference' if reference is True else 'sample'
    for index, (file_number, cutoff_from, reference, outliers_for, category) in summary_df.iterrows():
        if cutoff_from == cutoff and outliers_for == marker and category == population:
            yield file_number


def main():
    filename = 'raw_data.xlsx' if GATE is False else os.path.join('scouts output', 'gated_population.xlsx')
    population_df = pd.read_excel(os.path.join(BASE_PATH, filename), index_col=0).astype(float)
    summary_df = pd.read_excel(os.path.join(SCOUTS_PATH, 'summary.xlsx'))
    plot(samples=SAMPLES, pop_01=POP_01, pop_02=POP_02, marker=MARKER, reference=REFERENCE, population_df=population_df,
         summary_df=summary_df, scouts_path=SCOUTS_PATH)


if __name__ == '__main__':
    main()
