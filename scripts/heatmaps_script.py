import os
import re
from typing import List, Optional

import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

CONTROL = 'Pre-Tx'
TREATMENT = 'Week4'
MARKERS = [
    '(La139)Di<NGFR-139 (v)>',
    '(Pm147)Di<BCAT-147 (v)>',
    '(Sm150)Di<SOX10-150 (v)>',
    '(Eu151)Di<MCAM-151 (v)>',
    '(Eu153)Di<S100B-153 (v)>',
    '(Gd156)Di<CXCR3-156>',
    # '(Tb159)Di<CD90-159 (v)>',
    '(Er162)Di<MET-162 (v)>',
    '(Dy163)Di<SOX2-163 (v)>',
    '(Dy164)Di<CD49F-164 (v)>',
    '(Ho165)Di<EGFR-165 (v)>',
    '(Er166)Di<CD44-166 (v)>',
    '(Er168)Di<NES-168 (v)>',
    # '(Yb174)Di<HLA-DR-174 (v)>',
    '(Lu175)Di<PD-L1-175 (v)>',
    '(Lu176)Di<H3-176>'
    ]
DIRNAME = '../local/sample data/MP29_CD45low/scouts output'
FILENAME = 'stats.xlsx'
PLOT_NAME = 'name'

# Analysis & output parameters
PARAMS = {
    'log_heatmap': {
        'heatmap': None,
        'colormap': getattr(matplotlib.cm, 'RdBu_r'),
        'normalize': True,
        'global_normalize': True,
        'center': None,
        'ylabels': [
            'PreTx pop',
            'Week4 pop',
            'PreTx out',
            'Week4 out',
            'PreTx nonout',
            'Week4 nonout'
        ]
    },
    'ratio_heatmap': {
        'heatmap': None,
        'colormap': getattr(matplotlib.cm, 'BrBG'),
        'normalize': False,
        'global_normalize': False,
        'center': None,
        'ylabels': [
            r'$\frac{Week4\ pop}{PreTx\ pop}$',
            r'$\frac{Week4\ out}{PreTx\ out}$',
            r'$\frac{Week4\ nonout}{PreTx\ nonout}$',
            r'$\frac{Week4\ \frac{out}{nonout}}{PreTx\ \frac{out}{nonout}}$'
        ]
    },
    'out_heatmap': {
        'heatmap': None,
        'colormap': getattr(matplotlib.cm, 'PiYG'),
        'normalize': True,
        'global_normalize': True,
        'center': None,
        'ylabels': [
            r'PreTx $\frac{out}{nonout}$',
            r'Week4 $\frac{out}{nonout}$'
        ]
    }
}


def main(dirname: str, filename: str, ct: str, treat: str, markers: List[str]) -> None:
    """Main function for this script."""
    # load dataframe
    df = pd.read_excel(os.path.join(dirname, filename), index_col=[0, 1, 2], sheet_name='OutS single marker')
    control = df.loc[ct].loc[:, markers]
    treatment = df.loc[treat].loc[:, markers]

    # log heatmap
    log_heatmap = pd.DataFrame([
        np.log2(control.loc['whole population'].loc['mean']),
        np.log2(treatment.loc['whole population'].loc['mean']),
        np.log2(control.loc['top outliers'].loc['mean']),
        np.log2(treatment.loc['top outliers'].loc['mean']),
        np.log2(control.loc['non-outliers'].loc['mean']),
        np.log2(treatment.loc['non-outliers'].loc['mean'])])
    PARAMS['log_heatmap']['heatmap'] = log_heatmap

    # ratio heatmap
    ratio_heatmap = pd.DataFrame([
        np.log2(treatment.loc['whole population'].loc['mean']) / np.log2(control.loc['whole population'].loc['mean']),
        np.log2(treatment.loc['top outliers'].loc['mean']) / np.log2(control.loc['top outliers'].loc['mean']),
        np.log2(treatment.loc['non-outliers'].loc['mean']) / np.log2(control.loc['non-outliers'].loc['mean']),
        np.log2(treatment.loc['top outliers'].loc['mean'] / treatment.loc['non-outliers'].loc['mean']) / np.log2(
            control.loc['top outliers'].loc['mean'] / control.loc['non-outliers'].loc['mean'])
            ])
    PARAMS['ratio_heatmap']['heatmap'] = ratio_heatmap

    # out/non-out heatmap
    out_heatmap = pd.DataFrame([
        np.log2(control.loc['top outliers'].loc['mean'] / control.loc['non-outliers'].loc['mean']),
        np.log2(treatment.loc['top outliers'].loc['mean'] / treatment.loc['non-outliers'].loc['mean'])])
    PARAMS['out_heatmap']['heatmap'] = out_heatmap

    # plot data
    for heatmap_dict in PARAMS.values():
        heatmap = heatmap_dict['heatmap']
        colormap = heatmap_dict['colormap']
        ylabels = heatmap_dict['ylabels']
        normalize = heatmap_dict['normalize']
        global_normalize = heatmap_dict['global_normalize']
        center = heatmap_dict['center']
        plot_heatmap(heatmap=heatmap, colormap=colormap, markers=markers, ylabels=ylabels, normalize=normalize,
                     global_normalize=global_normalize, center=center)
    plt.show()


def parse_column_name(col: str) -> str:
    """parses column name from CyToF patient dataset."""
    return ''.join(re.search('Di<.*', col).group(0)[3:].split('-')[:-1])


def plot_heatmap(heatmap: pd.DataFrame, colormap: plt.cm, markers: List[str], ylabels: List[str],
                 normalize: bool, global_normalize: bool, center: Optional[float]) -> None:
    """Plots the heatmap into a separate figure"""
    if normalize is True:
        if global_normalize is True:
            heatmap = apply_global_normalize(heatmap)
        else:
            heatmap = apply_normalize(heatmap)
    fig = plt.figure()
    if center is not None:
        sns.heatmap(ax=fig.gca(), data=heatmap, square=True, xticklabels=1, linewidths=0.1, cmap=colormap,
                    center=center)
    else:
        sns.heatmap(ax=fig.gca(), data=heatmap, square=True, xticklabels=1, linewidths=0.1, cmap=colormap)
    plt.gca().set_xticklabels([parse_column_name(m) for m in markers])
    plt.gca().set_yticklabels(ylabels)
    return fig


def apply_global_normalize(heatmap: pd.DataFrame) -> pd.DataFrame:
    """Normalizes whole DataFrame to range [-1, 1]"""
    heat_max = np.nanmax(heatmap.values)
    heat_min = np.nanmin(heatmap.values)
    return (2 * (heatmap - heat_min)) / (heat_max - heat_min) - 1


def apply_normalize(heatmap: pd.DataFrame) -> pd.DataFrame:
    """Normalizes each DataFrame column to range [-1, 1]"""
    return heatmap.apply(lambda x: (2 * (x - x.min())) / (x.max() - x.min()) - 1)


if __name__ == '__main__':
    main(dirname=DIRNAME, filename=FILENAME, ct=CONTROL, treat=TREATMENT, markers=MARKERS)
