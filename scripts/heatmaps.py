import os
import re
from typing import List, Optional

import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Input parameters
GIO_DATASET = True
if GIO_DATASET is True:
    FILE_DIR = 'cytof gio'
    CONTROL = 'Ct'
    TREATMENT = 'RT'
else:
    FILE_DIR = 'MP29_CD45low'
    CONTROL = 'Pre-Tx'
    TREATMENT = 'Week4'
SAMPLES = [CONTROL, TREATMENT]
SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
FILENAME = 'stats.xlsx'
PATH = os.path.join(SCRIPT_DIR, '..', 'local', 'sample data', FILE_DIR, 'scouts output')

# Colormap parameters
CMAP = getattr(matplotlib.cm, 'RdBu_r')
# Analysis & output parameters
LOG2_TRANSFORM = True
LOG2_FIRST = True
NORMALIZE = True
GLOBAL_NORMALIZE = True
LABEL_NANS = True
SAVE_HEATMAPS = False
PLOT_HEATMAPS = True


def main(path: str, filename: str, ct: str, treat: str, samples: List[str], plot_name: Optional[str] = None) -> None:
    """Main function for this script."""
    # load dataframe
    df = pd.read_excel(os.path.join(path, filename), index_col=[0, 1, 2])
    if not GIO_DATASET:  # format column names nicely
        df.rename(columns={col: parse_column_name(col) for col in df.columns}, inplace=True)
    control = df.loc[ct]
    treatment = df.loc[treat]
    # first image
    populations = ['Whole population', 'Outliers', 'Non-outliers']
    index = pd.MultiIndex.from_product([samples, populations])
    first_heatmap = pd.DataFrame([pd.Series(control.loc['whole population'].loc['mean']),
                                  pd.Series(control.loc['top outliers'].loc['mean']),
                                  pd.Series(control.loc['non-outliers'].loc['mean']),
                                  pd.Series(treatment.loc['whole population'].loc['mean']),
                                  pd.Series(treatment.loc['top outliers'].loc['mean']),
                                  pd.Series(treatment.loc['non-outliers'].loc['mean'])],
                                 index=index)
    # second image
    out_non_out_ct = abs(control.loc['top outliers'].loc['mean'] / control.loc['non-outliers'].loc['mean'])
    out_non_out_rt = abs(treatment.loc['top outliers'].loc['mean'] / treatment.loc['non-outliers'].loc['mean'])
    index = [f'{ct} Out/Non-Out', f'{treat} Out/Non-Out']
    second_heatmap = pd.DataFrame([pd.Series(out_non_out_ct), pd.Series(out_non_out_rt)], index=index)
    # third image
    ruouta = abs(out_non_out_rt / out_non_out_ct)
    mean_rt_ct = abs(treatment.loc['whole population'].loc['mean'] / control.loc['whole population'].loc['mean'])
    index = [f'Relative Out/Non-Out', f'Mean {treat}/Mean {ct}']
    third_heatmap = pd.DataFrame([pd.Series(ruouta), pd.Series(mean_rt_ct)], index=index)
    # all heatmaps
    heatmaps = [first_heatmap, second_heatmap, third_heatmap]
    # export heatmaps
    if SAVE_HEATMAPS:
        output_filename = 'heatmaps.xlsx'
        writer = pd.ExcelWriter(os.path.join(path, output_filename))
        for index, heatmap in enumerate(heatmaps, 1):
            heatmap.to_excel(writer, sheet_name=f'heatmap_0{index}')
        writer.save()
    # plot heatmaps
    if PLOT_HEATMAPS:
        fig, axes = plt.subplots(3, 1, squeeze=True)
        plot_first_heatmap(heatmap=heatmaps[0], ax=axes[0])
        plot_second_heatmap(heatmap=heatmaps[1], ax=axes[1])
        plot_third_heatmap(heatmap=heatmaps[2], ax=axes[2])
        if plot_name is not None:
            fig.suptitle(plot_name)
        plt.show()


def parse_column_name(col: str) -> str:
    """parses column name from CyToF dataset."""
    return ''.join(re.search('Di<.*', col).group(0)[3:].split('-')[:-1])


def plot_first_heatmap(heatmap: pd.DataFrame, ax: plt.Axes) -> None:
    """Plots the top heatmap in the output figure."""
    expression = 'expression'
    if LOG2_TRANSFORM and LOG2_FIRST:
        expression = 'log2(expression)'
        heatmap = np.log2(heatmap)
    label = f'raw {expression}'
    if NORMALIZE:
        label = f'{expression} (normalized for each marker)'
        if GLOBAL_NORMALIZE:
            label = f'{expression} (normalized across all markers)'
            heat_max = np.nanmax(heatmap.values)
            heat_min = np.nanmin(heatmap.values)
            heatmap = (2 * (heatmap - heat_min)) / (heat_max - heat_min) - 1
        else:
            heatmap = heatmap.apply(lambda x: (2*(x - x.min()))/(x.max() - x.min()) - 1)

    sns.heatmap(data=heatmap, ax=ax, cmap=CMAP, square=False, xticklabels=1, linewidths=0.1, vmin=-1, vmax=1)
    if LABEL_NANS:
        data_labels = heatmap.isnull().replace({True: 'no data', False: ''})
        nan_data = pd.DataFrame(1.0, index=data_labels.index, columns=data_labels.columns)
        sns.heatmap(data=nan_data, ax=ax, cmap='binary', center=1.0, linewidths=0.1, mask=heatmap.notnull(),
                    cbar=False, annot=data_labels, annot_kws={'color': 'k', 'size': 6}, fmt='', xticklabels=1)
    cbar = ax.collections[0].colorbar
    cbar.set_label(label)
    cbar.set_ticks([-0.99, 0, 1.0])
    cbar.set_ticklabels(['-1.0', '0.0', '1.0'])
    ax.set_ylabel('')


def plot_second_heatmap(heatmap: pd.DataFrame, ax: plt.Axes) -> None:
    """Plots the middle heatmap in the output figure."""
    label = 'ratio'
    if LOG2_TRANSFORM:
        label = 'log2(ratio)'
        heatmap = np.log2(heatmap)
    sns.heatmap(data=heatmap, ax=ax, cmap=CMAP, square=True, xticklabels=1, linewidths=0.1)
    cbar = ax.collections[0].colorbar
    cbar.set_label(label)
    if LABEL_NANS:
        data_labels = heatmap.isnull().replace({True: 'no data', False: ''})
        nan_data = pd.DataFrame(1.0, index=data_labels.index, columns=data_labels.columns)
        sns.heatmap(data=nan_data, ax=ax, cmap='binary', center=1.0, square=True, linewidths=0.1,
                    mask=heatmap.notnull(), cbar=False, annot=data_labels, annot_kws={'color': 'k', 'size': 6},
                    fmt='', yticklabels=nan_data.index, xticklabels=1)


def plot_third_heatmap(heatmap: pd.DataFrame, ax: plt.Axes) -> None:
    """Plots the bottom heatmap in the output figure."""
    return plot_second_heatmap(heatmap=heatmap, ax=ax)


if __name__ == '__main__':
    main(path=PATH, filename=FILENAME, ct=CONTROL, treat=TREATMENT, samples=SAMPLES, plot_name=FILE_DIR)
