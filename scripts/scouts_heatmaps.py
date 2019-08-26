from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING, Tuple
import os
import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

CONTROL = 'Ct'
TREATMENT = 'RT'
SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
CMAP_STR = 'RdBu_r'
CMAP = getattr(matplotlib.cm, CMAP_STR)
CMAP.set_bad('gray')

SHEET = 'OutS single marker'
LOG_TRANSFORM = True
TRUE = True


class DataFrameDict(dict):
    def __init__(self, df, ct, treat) -> None:
        super().__init__()
        self.df = df
        self['markers'] = list(df.columns)
        self[ct] = self.get_samples(ct)
        self[ct]['population'] = self.get_population_data(ct)
        self[treat] = self.get_samples(treat)
        self[treat]['population'] = self.get_population_data(treat)

    def get_samples(self, cond) -> Dict[str, pd.DataFrame]:
        d = {}
        for pos in ('top outliers', 'bottom outliers', 'non-outliers'):
            d[pos] = self.df.loc[cond].loc[pos]
        return d

    def get_population_data(self, cond) -> pd.DataFrame:
        df = pd.DataFrame(0.0, index=['#', 'mean', 'median', 'sd'], columns=self['markers'])
        for marker in self['markers']:
            n = []
            for name, cond_df in self[cond].items():
                num = cond_df[marker].loc['#']
                df[marker].loc['#'] += num
                df[marker].loc[['mean', 'median', 'sd']] += cond_df[marker].loc['mean', 'median', 'sd'] * num
                n.append(num)
            df[marker].loc[['mean', 'median', 'sd']] = df[marker].loc[['mean', 'median', 'sd']] / sum(n)
        return df


def main(path: str, ct: str, treat: str, sheet_name: str) -> None:
    """Main function for this script."""
    df = pd.read_excel(path, index_col=[0, 1, 2], sheet_name=sheet_name)
    print(df)
    df_dict = DataFrameDict(df, ct, treat)
    print(df_dict['markers'])
    print(df_dict['control'])
    print(df_dict['treatment'])
    if TRUE:
        return

    fig, axes = plt.subplots(3, 1, squeeze=True)

    # first image
    samples = ['Ct', 'RT']
    populations = ['Whole population', 'Outliers', 'Non-outliers']
    index = pd.MultiIndex.from_product([samples, populations])
    first_heatmap = pd.DataFrame([pd.Series(controls['pop'].loc['mean']),
                                  pd.Series(controls['top'].loc['mean']),
                                  pd.Series(controls['non'].loc['mean']),
                                  pd.Series(treatments['pop'].loc['mean']),
                                  pd.Series(treatments['top'].loc['mean']),
                                  pd.Series(treatments['non'].loc['mean'])],
                                 index=index)
    plot_heatmap(first_heatmap, axes[0])

    # second image
    out_non_out_ct = controls['top'].loc['mean'] / controls['non'].loc['mean']
    out_non_out_rt = treatments['top'].loc['mean'] / treatments['non'].loc['mean']
    index = ['Ct Out/Non-Out', 'RT Out/Non-Out']
    second_heatmap = pd.DataFrame([pd.Series(out_non_out_ct), pd.Series(out_non_out_rt)], index=index)
    plot_heatmap(second_heatmap, axes[1])

    # third image
    ruouta = out_non_out_rt / out_non_out_ct
    mean_rt_ct = treatments['pop'].loc['mean'] / controls['pop'].loc['mean']
    index = ['RUOutA', 'Mean RT/Mean Ct']
    second_heatmap = pd.DataFrame([pd.Series(ruouta), pd.Series(mean_rt_ct)], index=index)
    plot_heatmap(second_heatmap, axes[2])
    plt.show()


def plot_heatmap(arr: np.array, ax: plt.Axes):
    img = sns.heatmap(data=arr, ax=ax, cmap=CMAP, square=True)
    return img


if __name__ == '__main__':
    # args = get_args()
    main(path=os.path.join(SCRIPT_DIR, '..', 'local', 'output', 'stats.xlsx'), ct=CONTROL, treat=TREATMENT,
         sheet_name=SHEET)










