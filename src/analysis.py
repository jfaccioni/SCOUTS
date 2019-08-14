from __future__ import annotations

import os
from pprint import pprint
from typing import List, Tuple, TYPE_CHECKING, Optional, Dict

import numpy as np
import pandas as pd

from src.custom_exceptions import PandasInputError, SampleNamingError, NoReferenceError

# Pandas DataFrame options (this goes to logfile)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('expand_frame_repr', False)

if TYPE_CHECKING:
    from PySide2.QtWidgets import QMainWindow


def analyse(widget: QMainWindow, input_file: str, output_folder: str, cutoff_rule: str,
            marker_rule: str, tukey_factor: float, export_csv: bool, export_excel: bool,
            single_excel: bool, sample_list: List[Tuple[str, str]], gate_cutoff: Optional[float],
            non_outliers: bool, bottom_outliers: bool):
    # Loads df and checks for file extension
    df = load_dataframe(input_file=input_file)
    if df is None:
        raise PandasInputError(widget)
    # Checks if all sample names are in at least one cell of the first column in the df
    all_sample_names_are_in_df = check_sample_names(sample_list=sample_list, df=df)
    if all_sample_names_are_in_df is False:
        raise SampleNamingError(widget)
    # Apply gates to df, if any
    if gate_cutoff is not None:
        if widget.cytof_gates.isChecked():
            apply_cytof_gating(df=df, cutoff=gate_cutoff)
        elif widget.rnaseq_gates.isChecked():
            apply_rnaseq_gating(df=df, cutoff=gate_cutoff)
    # Gets cutoff dict -> { 'sample' : { 'marker' : (Q1, Q3, IQR, CUTOFF_LOW, CUTOFF_HIGH) } }
    cutoff_dict = get_cutoff_values(df=df, sample_list=sample_list, cutoff_rule=cutoff_rule, tukey=tukey_factor)
    pprint(cutoff_dict)
    # Change directory to output directory, open log file
    # os.chdir(output_folder)
    # if 'log' not in os.listdir(os.getcwd()):
    #     os.mkdir('log')
    # f = open(os.path.join('log', 'outlier_analysis_log.txt'), 'w')
    # # Save all cutoff values as pretty-printed dictionary
    # f.write('CUTOFF VALUES AS A DICTIONARY:\n')
    # f.write('the data is ordered as:\n\n')
    # f.write("{ 'sample' : { 'marker' : (. . .) } }\n")
    # f.write("(. . .) represent this tuple: ")
    # f.write("(Q1, Q3, IQR, (upper cutoff, lower cutoff)\n\n")
    # pprint(sample_dict, stream=f, width=120)
    # f.write('\n\n')
    # # Iterate over yield_dataframes function, subsetting DataFrames and saving
    # # each DataFrame to a different file
    # df_list = []
    # for dataframe, *names in yield_dataframes(log=f, df=df, sample_dict=sample_dict, control=control,
    #                                           outliers=cutoff_rule, by_marker=marker_rule,
    #                                           bottom_outliers=bottom_outliers):
    #     m, s, n, c = names
    #     population_df = None
    #     if non_outliers:
    #         population_df = get_inverse_df(df, dataframe)
    #     # Create subfolder in output directory for each sample
    #     if s not in os.listdir(os.getcwd()):
    #         os.mkdir(s)
    #     main_name = f'{m}_{s}_{c}_cutoff_by_{n}'
    #     # avoids error when marker name has / or \ in it
    #     main_name = main_name.replace('\\', '_')
    #     main_name = main_name.replace('/', '_')
    #     output = os.path.join(s, f'{main_name}')
    #     if export_csv:
    #         dataframe.to_csv(f'{output}.csv', index=False)
    #         if population_df is not None:
    #             population_df.to_csv(f'{output}_pop.csv', index=False)
    #     if export_excel:
    #         dataframe.to_excel(f'{output}.xlsx', sheet_name=m, index=False)
    #         if population_df is not None:
    #             population_df.to_excel(f'{output}_pop.xlsx', sheet_name=m, index=False)
    #         if single_excel:
    #             df_list.append((dataframe, main_name))
    #             if population_df is not None:
    #                 df_list.append((population_df, main_name + '_pop'))
    #
    # # Close log file
    # f.close()
    # # Save master excel file
    # if df_list:
    #     writer = pd.ExcelWriter('master_output.xlsx')
    #     for dataframe, name in df_list:
    #         dataframe.to_excel(writer, name, index=False)
    #     writer.save()


def check_sample_names(sample_list: List[Tuple[str, str]], df: pd.DataFrame) -> Optional[int]:
    sample_names = list(df.iloc[:, 0])  # Assumes first column = sample names (as per documentation)
    for sample,  _ in sample_list:
        if not any(sample in name for name in sample_names):
            return False
    return True


def load_dataframe(input_file: str) -> Optional[pd.DataFrame]:
    if input_file.endswith('.xlsx') or input_file.endswith('xls'):
        return pd.read_excel(input_file, header=0)
    elif input_file.endswith('.csv'):
        return pd.read_csv(input_file, header=0)
    return None


def apply_cytof_gating(df: pd.DataFrame, cutoff: float) -> None:
    indices_to_drop = []
    for index, row in df.iterrows():
        mean_row_value = np.mean(row[1:])  # first row contains sample names
        if mean_row_value <= cutoff:
            indices_to_drop.append(index)
    df.drop(indices_to_drop, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)


def apply_rnaseq_gating(df: pd.DataFrame, cutoff: float) -> None:
    df.mask(df <= cutoff, np.nan, inplace=True)


def get_cutoff_values(df: pd.DataFrame, sample_list: List[Tuple[str, str]], cutoff_rule: str, tukey: float) -> Dict:
    if cutoff_rule == 'reference':
        reference = get_reference_sample_name(sample_list)
        if reference is None:
            raise NoReferenceError  # If the user chose to analyse by reference but hadn't selected any reference
        reference_dict = get_cutoff_values_for_single_sample(df=df, sample=reference, tukey=tukey)
        return {reference: reference_dict}
    elif cutoff_rule == 'sample':
        samples = get_all_sample_names(sample_list)
        return get_cutoff_values_for_all_samples(df=df, samples=samples, tukey=tukey)


def get_reference_sample_name(sample_list: List[Tuple[str, str]]) -> Optional[str]:
    for sample, sample_type in sample_list:
        if sample_type == 'Yes':
            return sample
    return None


def get_all_sample_names(sample_list: List[Tuple[str, str]]) -> List[str]:
    return [tup[0] for tup in sample_list]


def get_cutoff_values_for_single_sample(df: pd.DataFrame, sample: str, tukey: float):
    reference_dict = {}
    filtered_df = df[df.iloc[:, 0].str.contains(sample)]
    quantile_df = filtered_df.quantile([0.25, 0.75])
    for marker in quantile_df:
        reference_dict[marker] = get_sample_statistics(tukey=tukey, marker_series=quantile_df[marker])
    return reference_dict


def get_cutoff_values_for_all_samples(df: pd.DataFrame, samples: List[str], tukey: float):
    sample_dict = {}
    for sample in samples:
        markers_dict = get_cutoff_values_for_single_sample(df=df, sample=sample, tukey=tukey)
        sample_dict[sample] = markers_dict
    return sample_dict


def get_sample_statistics(tukey, marker_series: pd.Series) -> Tuple[float, float, float, float, float]:
    first_quartile, third_quartile = marker_series
    iqr = third_quartile - first_quartile
    upper_cutoff = third_quartile + (iqr * tukey)
    lower_cutoff = first_quartile - (iqr * tukey)
    return first_quartile, third_quartile, iqr, lower_cutoff, upper_cutoff


def yield_dataframes(log, df, sample_dict, control, outliers, by_marker, bottom_outliers):
    # ###
    # ### RULE: outliers by control cutoff, outliers for a single marker
    # ###
    if outliers in ('control', 'both') and by_marker in ('marker', 'both'):
        log.write('------- CUTOFF BY CONTROL, OUTLIERS BY MARKER -------\n\n\n')
        for sample, _ in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, (cutoff)) in sample_dict[control].items():
                cut = cutoff[0]
                cut_text = 'top'
                output_df = filtered_df.loc[filtered_df[marker] > cut]
                log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                log.write('METHOD: use control cutoff, ')
                log.write('check outliers for current marker only\n')
                log.write(f'CUTOFF: {cutoff}\n')
                log.write(f'OUTLIERS: from {cut_text}')
                log.write('\n\n')
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, marker, sample, 'control', cut_text
                if bottom_outliers:
                    cut = cutoff[1]
                    cut_text = 'bottom'
                    output_df = filtered_df.loc[filtered_df[marker] < cut]
                    log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                    log.write('METHOD: use control cutoff, ')
                    log.write('check outliers for current marker only\n')
                    log.write(f'CUTOFF: {cutoff}\n')
                    log.write(f'OUTLIERS: from {cut_text}')
                    log.write('\n\n')
                    log.write(str(output_df))
                    log.write('\n\n\n\n')
                    yield output_df, marker, sample, 'control', cut_text
    # ###
    # ### RULE: outliers by control cutoff, outliers for any marker in row
    # ###
    if outliers in ('control', 'both') and by_marker in ('row', 'both'):
        log.write('------- CUTOFF BY CONTROL, OUTLIERS BY ROW -------\n\n\n')
        for sample, _ in sample_dict.items():
            log.write(f'SAMPLE: {sample}\n')
            log.write('METHOD: use control cutoff, ')
            log.write('check outliers for any markers in whole row\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            cut_text = 'top'
            for marker, (*_, (cutoff)) in sample_dict[control].items():
                cut = cutoff[0]
                log.write(f'OUTLIERS: from {cut_text}')
                log.write('\n\n')
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cut]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            log.write(str(output_df))
            log.write('\n\n\n\n')
            yield output_df, 'all_markers', sample, 'control', cut_text
            if bottom_outliers:
                cut_text = 'bottom'
                for marker, (*_, (cutoff)) in sample_dict[control].items():
                    cut = cutoff[1]
                    log.write(f'OUTLIERS: from {cut_text}')
                    log.write('\n\n')
                    cutoff_rows = filtered_df.loc[filtered_df[marker] < cut]
                    output_df = output_df.append(cutoff_rows, sort=False)
                output_df.drop_duplicates(inplace=True)
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, 'all_markers', sample, 'control', cut_text
    # ###
    # ### RULE: outliers by sample cutoff, outliers for a single marker
    # ###
    if outliers in ('sample', 'both') and by_marker in ('marker', 'both'):
        log.write('------- CUTOFF BY SAMPLE, OUTLIERS BY MARKER -------\n\n\n')
        for sample, mkdict in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, (cutoff)) in mkdict.items():
                cut = cutoff[0]
                cut_text = 'top'
                output_df = filtered_df.loc[filtered_df[marker] > cut]
                log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                log.write('METHOD: use sample cutoff, ')
                log.write('check outliers for current marker only\n')
                log.write(f'CUTOFF: {cutoff}\n')
                log.write(f'OUTLIERS: from {cut_text}')
                log.write('\n\n')
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, marker, sample, 'sample', cut_text
                if bottom_outliers:
                    cut = cutoff[1]
                    cut_text = 'bottom'
                    output_df = filtered_df.loc[filtered_df[marker] < cut]
                    log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                    log.write('METHOD: use sample cutoff, ')
                    log.write('check outliers for current marker only\n')
                    log.write(f'CUTOFF: {cutoff}\n')
                    log.write(f'OUTLIERS: from {cut_text}')
                    log.write('\n\n')
                    log.write(str(output_df))
                    log.write('\n\n\n\n')
                    yield output_df, marker, sample, 'sample', cut_text
    # ###
    # ### RULE: outliers by sample cutoff, outliers for any marker in row
    # ###
    if outliers in ('sample', 'both') and by_marker in ('row', 'both'):
        log.write('------- CUTOFF BY SAMPLE, OUTLIERS BY ROW -------\n\n\n')
        for sample, mkdict in sample_dict.items():
            log.write(f'SAMPLE: {sample}')
            log.write('METHOD: use sample cutoff, ')
            log.write('check outliers for any markers in whole row')
            log.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            cut_text = 'top'
            for marker, (*_, (cutoff)) in mkdict.items():
                cut = cutoff[0]
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cut]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            log.write(str(output_df))
            log.write('\n\n\n\n')
            yield output_df, 'all_markers', sample, 'sample', cut_text
            if bottom_outliers:
                cut_text = 'bottom'
                for marker, (*_, (cutoff)) in mkdict.items():
                    cut = cutoff[1]
                    cutoff_rows = filtered_df.loc[filtered_df[marker] < cut]
                    output_df = output_df.append(cutoff_rows, sort=False)
                output_df.drop_duplicates(inplace=True)
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, 'all_markers', sample, 'sample', cut_text


def get_inverse_df(full_df, partial_df):
    df_merge = full_df.merge(partial_df.drop_duplicates(), on=list(full_df), how='left', indicator=True)
    inverse_df = full_df[df_merge['_merge'] == 'left_only']
    return inverse_df
