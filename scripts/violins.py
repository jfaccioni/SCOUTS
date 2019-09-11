import os
from typing import Generator, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Plot styling
sns.set(style="whitegrid")

# Project root (SCOUTS main folder)
SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')

# Input directory (directory containing file with whole population prior to SCOUTS)
SCOUTS_INPUT_FOLDER = os.path.join(PROJECT_ROOT, 'local', 'sample data', 'cytof gio')
POPULATION_FILE = 'gio-mass-cytometry.xlsx'
SCOUTS_POPULATION_FILENAME = os.path.join(SCOUTS_INPUT_FOLDER, POPULATION_FILE)

# Output directory (directory used to save SCOUTS results)
SCOUTS_OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, 'local', 'sample data', 'cytof gio', 'scouts output')
SUMMARY_FILE = 'summary.xlsx'
SCOUTS_SUMMARY_FILENAME = os.path.join(SCOUTS_OUTPUT_FOLDER, SUMMARY_FILE)

# Comparison options
POPULATION_TO_COMPARE = 'top outliers'
SAMPLES_TO_COMPARE = ['Ct', 'RT', 'Torin']
MARKERS_TO_COMPARE = ['CD44']  # only one marker at a time!
CONSIDER_WHOLE_POPULATION = False
CUTOFF_FROM_REFERENCE = False


def main(population_path: str, summary_path: str, output_folder: str, population: str, samples: List[str],
         markers: List[str], consider_whole_population: bool, cutoff_from_reference: bool) -> None:
    """Main function for this script."""
    # Create DataFrame for adding results for plotting the violins
    columns = ['sample', 'marker', 'population', 'expression']
    violin_df = pd.DataFrame(columns=columns)

    # Get DataFrame for finding results file
    summary_df = pd.read_excel(summary_path, index_col=None)

    # Compare outliers to whole population
    if consider_whole_population:
        population_df = pd.read_excel(population_path, index_col=0)
        for partial_df in yield_violin_values(df=population_df, population='whole population', samples=samples,
                                              markers=markers, columns=columns):
            violin_df = violin_df.append(partial_df)

    # Compare outliers to non-outlier population
    else:
        for file_number in yield_selected_file_numbers(summary_df=summary_df, population='non-outliers',
                                                       cutoff_from_reference=cutoff_from_reference, markers=markers):
            df_path = os.path.join(output_folder, 'data', f'{"%04d" % file_number}.csv')
            sample_df = pd.read_csv(df_path, index_col=0)
            for partial_df in yield_violin_values(df=sample_df, population='non-outliers', samples=samples,
                                                  markers=markers, columns=columns):
                violin_df = violin_df.append(partial_df)

    # Get outlier values
    for file_number in yield_selected_file_numbers(summary_df=summary_df, population=population,
                                                   cutoff_from_reference=cutoff_from_reference, markers=markers):
        df_path = os.path.join(output_folder, 'data', f'{"%04d" % file_number}.csv')
        sample_df = pd.read_csv(df_path, index_col=0)
        for partial_df in yield_violin_values(df=sample_df, population=population, samples=samples,
                                              markers=markers, columns=columns):
            violin_df = violin_df.append(partial_df)

    # Plot violins
    for marker in markers:
        fig = plt.figure()
        fig.suptitle(f'{marker} expression')
        populations = violin_df.population.unique()
        subset_by_marker = violin_df[violin_df['marker'] == marker]
        for pop in populations:
            subset_by_pop = subset_by_marker.loc[subset_by_marker['population'] == pop]
            color = [0.4, 0.76078431, 0.64705882] if pop != population else [0.98823529, 0.55294118, 0.38431373]
            for sample in samples:
                subset_by_sample = subset_by_pop.loc[subset_by_pop['sample'] == sample]
                sat = 1.0 - samples.index(sample)/(len(samples)+1)
                sns.violinplot(data=subset_by_sample, x='sample', y='expression',
                               color=color, saturation=sat, order=samples)
    plt.show()


def yield_violin_values(df: pd.DataFrame, population: str, samples: List[str], markers: List[str],
                        columns: List[str]) -> pd.DataFrame:
    """Returns a DataFrame from expression values, along with information of sample, marker and population. This
    DataFrame is appended to the violin plot DataFrame in order to simplify plotting the violins afterwards."""
    for sample in samples:
        for marker in markers:
            series = df.loc[df.index.str.contains(sample)].loc[:, marker]
            yield pd.DataFrame({'sample': sample, 'marker': marker, 'population': population, 'expression': series},
                               columns=columns)


def yield_selected_file_numbers(summary_df: pd.DataFrame, population: str, cutoff_from_reference: bool,
                                markers: List[str]) -> Generator[pd.DataFrame, None, None]:
    """Yields file numbers from DataFrames resulting from SCOUTS analysis. DataFrames are yielded based on
    global values, i.e. the comparisons the user wants to perform."""
    cutoff = 'sample'
    if cutoff_from_reference:
        cutoff = 'reference'
    for index, (file_number, cutoff_from, reference, outliers_for, category) in summary_df.iterrows():
        if cutoff_from == cutoff and outliers_for in markers and category == population:
            yield file_number


if __name__ == '__main__':
    main(population_path=SCOUTS_POPULATION_FILENAME,
         summary_path=SCOUTS_SUMMARY_FILENAME,
         output_folder=SCOUTS_OUTPUT_FOLDER,
         population=POPULATION_TO_COMPARE,
         samples=SAMPLES_TO_COMPARE,
         markers=MARKERS_TO_COMPARE,
         consider_whole_population=CONSIDER_WHOLE_POPULATION,
         cutoff_from_reference=CUTOFF_FROM_REFERENCE)
