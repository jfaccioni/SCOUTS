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

SHEET = ['OutS single marker']
OUTLIERS_TO_COMPARE = ['top', 'non']

LOG_TRANSFORM = True


class DataFrameDict(dict):
    def __init__(self) -> None:
        super().__init__()

    @property
    def markers(self):
        return self.get('markers')

    def get_dfs(self, *substrings: str) -> List[pd.DataFrame]:
        return [v for d, v in self.items() if any(substring in d for substring in substrings)]

    def get_controls(self) -> Dict[str, pd.DataFrame]:
        return {name: df for name, df in zip(('pop', 'top', 'non'), self.get_dfs(CONTROL))}

    def get_treatments(self) -> Dict[str, pd.DataFrame]:
        return {name: df for name, df in zip(('pop', 'top', 'non'), self.get_dfs(TREATMENT))}

    def get_names(self, *substrings: str) -> List[str]:
        return [d for d, v in self.items() if any(substring in d for substring in substrings)]

    def get_items(self, *substrings: str) -> List[Tuple[str, pd.DataFrame]]:
        return [(d, v) for d, v in self.items() if any(substring in d for substring in substrings)]


def main(path: str, ct: str, treat: str, sheet_name: List[str], outliers: List[str]) -> None:
    """Main function for this script."""
    df_dict = DataFrameDict()
    df = pd.read_excel(path, index_col=[0, 1, 2], sheet_name=sheet_name)
    df_dict['markers'] = list(df.columns)
    for condition in [ct, treat]:
        for outlier_position in ['top outliers', 'non-outliers', 'bottom outliers']:
            df_dict[f"{condition}_{outlier_position}"] = df.loc[condition].loc[outlier_position]
            # add population info
        df_dict[f"{condition}_pop"] = (df_dict[f"{condition}_top outliers"] +
                                        df_dict[f"{condition}_non-outliers"] +
                                        df_dict[f"{condition}_bottom outliers"])

    controls = df_dict.get_controls()
    treatments = df_dict.get_treatments()

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
    main(path=os.path.join(SCRIPT_DIR, '..', 'local', 'output', 'stats.xlsx'),
         ct=CONTROL,
         treat=TREATMENT,
         sheet_name=SHEET,
         outliers=OUTLIERS_TO_COMPARE)










