import os
import re
from typing import List

# noinspection PyUnresolvedReferences,PyPackageRequirements
import matplotlib.cm
# noinspection PyUnresolvedReferences,PyPackageRequirements
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# noinspection PyUnresolvedReferences, PyPackageRequirements
import seaborn as sns

# Main arguments
GIO_DATASET = True
SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

CONTROL = 'Ct'
TREATMENT = 'RT'
PATH = os.path.join(SCRIPT_DIR, '..', 'local', 'sample data', 'cytof gio')
FILENAME = 'gio-mass-cytometry-stats.xlsx'

if GIO_DATASET is False:
    PATH = os.path.join(SCRIPT_DIR, '..', 'local', 'sample data', 'MP29_CD45low')
    FILENAME = 'data_stats.xlsx'
    CONTROL = 'Pre-Tx'
    TREATMENT = 'Week4'

SAMPLES = [CONTROL, TREATMENT]

# Colormap options
CMAP_STR = 'RdBu_r'
# noinspection PyUnresolvedReferences
CMAP = getattr(matplotlib.cm, CMAP_STR)
CMAP.set_bad('gray')

# Analysis options
LOG_TRANSFORM = True

# Output options
SAVE_HEATMAPS = False
PLOT_HEATMAPS = True


def main(path: str, filename: str, ct: str, treat: str, samples: List[str]) -> None:
    """Main function for this script."""

    # load dataframe
    df = pd.read_excel(os.path.join(path, filename), index_col=[0, 1, 2])
    if not GIO_DATASET:
        df.rename(columns={col: parse_column_name(col) for col in df.columns}, inplace=True)
    control = df.loc[ct]
    treatment = df.loc[treat]
    fig, axes = plt.subplots(3, 1, squeeze=True)

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
    out_non_out_ct = control.loc['top outliers'].loc['mean'] / control.loc['non-outliers'].loc['mean']
    out_non_out_rt = treatment.loc['top outliers'].loc['mean'] / treatment.loc['non-outliers'].loc['mean']
    index = [f'{ct} Out/Non-Out', f'{treat} Out/Non-Out']
    second_heatmap = pd.DataFrame([pd.Series(out_non_out_ct), pd.Series(out_non_out_rt)], index=index)
    if LOG_TRANSFORM:
        second_heatmap = np.log(second_heatmap)

    # third image
    ruouta = out_non_out_rt / out_non_out_ct
    mean_rt_ct = treatment.loc['whole population'].loc['mean'] / control.loc['whole population'].loc['mean']
    index = ['Relative Out/Non-out', f'Mean {treat}/Mean {ct}']
    third_heatmap = pd.DataFrame([pd.Series(ruouta), pd.Series(mean_rt_ct)], index=index)
    if LOG_TRANSFORM:
        third_heatmap = np.log(third_heatmap)

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
        for index, heatmap in enumerate(heatmaps):
            sns.heatmap(data=heatmap, ax=axes[index], cmap=CMAP, square=True, xticklabels=1)
        plt.show()


def parse_column_name(col: str) -> str:
    """parses column name from CyToF dataset."""
    return ''.join(re.search('Di<.*', col).group(0)[3:].split('-')[:-1])


if __name__ == '__main__':
    main(path=PATH, filename=FILENAME, ct=CONTROL, treat=TREATMENT, samples=SAMPLES)
