import os

# noinspection PyUnresolvedReferences
import matplotlib.cm
# noinspection PyUnresolvedReferences
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# noinspection PyUnresolvedReferences, PyPackageRequirements
import seaborn as sns

# Main arguments
CONTROL = 'Ct'
TREATMENT = 'RT'
SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
PATH = os.path.join(SCRIPT_DIR, '..', 'local', 'giovana files')

# Colormap options
CMAP_STR = 'RdBu_r'
# noinspection PyUnresolvedReferences
CMAP = getattr(matplotlib.cm, CMAP_STR)
CMAP.set_bad('gray')

# Analysis options
LOG_TRANSFORM = True

# Output options
SAVE_HEATMAPS = True
PLOT_HEATMAPS = True


def main(path: str, ct: str, treat: str) -> None:
    """Main function for this script."""

    # load dataframe
    filename = 'gio-mass-cytometry-stats.xlsx'
    df = pd.read_excel(os.path.join(path, filename), index_col=[0, 1, 2])
    control = df.loc[ct]
    treatment = df.loc[treat]
    fig, axes = plt.subplots(3, 1, squeeze=True)

    # first image
    samples = ['Ct', 'RT']
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
    index = ['Ct Out/Non-Out', 'RT Out/Non-Out']
    second_heatmap = pd.DataFrame([pd.Series(out_non_out_ct), pd.Series(out_non_out_rt)], index=index)
    if LOG_TRANSFORM:
        second_heatmap = np.log(second_heatmap)

    # third image
    ruouta = out_non_out_rt / out_non_out_ct
    mean_rt_ct = treatment.loc['whole population'].loc['mean'] / control.loc['whole population'].loc['mean']
    index = ['RUOutA', 'Mean RT/Mean Ct']
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
            sns.heatmap(data=heatmap, ax=axes[index], cmap=CMAP, square=True)
        plt.show()


if __name__ == '__main__':
    main(path=PATH, ct=CONTROL, treat=TREATMENT)
