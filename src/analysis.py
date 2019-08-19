from __future__ import annotations

from collections import namedtuple
from typing import Generator, List, Optional, TYPE_CHECKING, Tuple

import numpy as np
import pandas as pd

from src.custom_exceptions import NoReferenceError, PandasInputError, SampleNamingError

# Pandas DataFrame options (this goes to logfile)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('expand_frame_repr', False)

if TYPE_CHECKING:
    from PySide2.QtWidgets import QMainWindow

Stats = namedtuple("Stats", ['first_quartile', 'third_quartile', 'iqr', 'lower_cutoff', 'upper_cutoff'])


# TODO: ### URGENT! Comparisons for any marker don't include the sample name (first row of input dataframe),
#  which causes the comparison to mismatch in size.


def analyse(widget: QMainWindow, input_file: str, output_folder: str, cutoff_rule: str,
            marker_rule: str, tukey_factor: float, export_csv: bool, export_excel: bool,
            single_excel: bool, sample_list: List[Tuple[str, str]], gate_cutoff: Optional[float],
            non_outliers: bool, bottom_outliers: bool):
    """Main SCOUTS function that organizes user input and calls related functions accordingly."""
    # Loads df and checks for file extension
    input_df = load_dataframe(widget=widget, input_file=input_file)
    # Checks if all sample names are in at least one cell of the first column in the df
    validate_sample_names(widget=widget, sample_list=sample_list, df=input_df)
    # Apply gates to df, if any
    if gate_cutoff is not None:
        if widget.cytof_gates.isChecked():
            apply_cytof_gating(df=input_df, cutoff=gate_cutoff)
        elif widget.rnaseq_gates.isChecked():
            apply_rnaseq_gating(df=input_df, cutoff=gate_cutoff)
    # Gets cutoff dict -> { 'sample' : { 'marker' : (Q1, Q3, IQR, CUTOFF_LOW, CUTOFF_HIGH) } }
    cutoff_df = get_cutoff_dataframe(df=input_df, sample_list=sample_list, cutoff_rule=cutoff_rule, tukey=tukey_factor)
    # generate outlier tables (SCOUTS)
    run_scouts(input_df=input_df, cutoff_df=cutoff_df, sample_list=sample_list, cutoff_rule=cutoff_rule,
               marker_rule=marker_rule, export_csv=export_csv, export_excel=export_excel, single_excel=single_excel,
               non_outliers=non_outliers, bottom_outliers=bottom_outliers, output_folder=output_folder)

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


def validate_sample_names(widget: QMainWindow, sample_list: List[Tuple[str, str]], df: pd.DataFrame) -> None:
    """Checks whether any sample name from the sample table isn't present on the input dataframe.
    Raises an exception if this happens."""
    sample_names = list(df.iloc[:, 0])  # Assumes first column = sample names (as per documentation)
    for sample,  _ in sample_list:
        if not any(sample in name for name in sample_names):
            raise SampleNamingError(widget)


def load_dataframe(widget: QMainWindow, input_file: str) -> pd.DataFrame:
    """Loads input dataframe into memory. Raises an exception if the filename doesn't end with
    .xlsx or .csv (supported formats)."""
    if input_file.endswith('.xlsx') or input_file.endswith('xls'):
        return pd.read_excel(input_file, header=0)
    elif input_file.endswith('.csv'):
        return pd.read_csv(input_file, header=0)
    else:
        raise PandasInputError(widget)


def apply_cytof_gating(df: pd.DataFrame, cutoff: float) -> None:
    """Applies gating for Mass Cytometry onto input dataframe, excluding rows with low average expression."""
    indices_to_drop = []
    for index, row in df.iterrows():
        mean_row_value = np.mean(row[1:])  # first row contains sample names
        if mean_row_value <= cutoff:
            indices_to_drop.append(index)
    df.drop(indices_to_drop, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)


def apply_rnaseq_gating(df: pd.DataFrame, cutoff: float) -> None:
    """Applies gating for Single-Cell RNASeq onto input dataframe, excluding values below threshold from
    calculations of outlier values."""
    df.mask(df <= cutoff, np.nan, inplace=True)


def get_cutoff_dataframe(df: pd.DataFrame, sample_list: List[Tuple[str, str]], cutoff_rule: str,
                         tukey: float) -> pd.DataFrame:
    """Gets a dataframe with cutoff values(Q1, Q3, IQR, CUTOFF_LOW, CUTOFF_HIGH) in which columns correspond
    to markers and rows (index) correspond to samples."""
    if cutoff_rule == 'ref':
        reference = get_reference_sample_name(sample_list=sample_list)
        return get_cutoff(df=df, samples=[reference], tukey=tukey)
    else:
        samples = get_all_sample_names(sample_list=sample_list)
        return get_cutoff(df=df, samples=samples, tukey=tukey)


def get_reference_sample_name(sample_list: List[Tuple[str, str]]) -> str:
    """Gets the name from the reference sample, raising an exception if it does not exist in the sample table."""
    for sample, sample_type in sample_list:
        if sample_type == 'Yes':
            return sample
    else:
        raise NoReferenceError  # If the user chose to analyse by reference but did not select any reference


def get_all_sample_names(sample_list: List[Tuple[str, str]]) -> List[str]:
    """Gets the name of all samples from the sample table."""
    return [tup[0] for tup in sample_list]


def get_marker_names_from_df(df: pd.DataFrame) -> List[str]:
    return list(df.columns[1:])


def get_cutoff(df: pd.DataFrame, samples: List[str], tukey: float) -> pd.DataFrame:
    """Gets cutoff values"""  # TODO
    result_df = pd.DataFrame(columns=get_marker_names_from_df(df=df), index=samples)
    for sample in samples:
        cutoff_values = get_sample_cutoff(df=df, sample=sample, tukey=tukey)
        result_df.loc[sample] = cutoff_values
    return result_df


def get_sample_cutoff(df: pd.DataFrame, sample: str, tukey: float) -> List[Tuple[float, float, float, float, float]]:
    """Gets sample cutoff"""  # TODO
    values = []
    filtered_df = filter_df_by_sample_name(df=df, sample=sample)
    quantile_df = filtered_df.quantile([0.25, 0.75])
    for marker in quantile_df:
        values.append(get_sample_statistics(tukey=tukey, marker_series=quantile_df[marker]))
    return values


def filter_df_by_sample_name(df: pd.DataFrame, sample: str) -> pd.DataFrame:
    return df[df.iloc[:, 0].str.contains(sample)]


def get_sample_statistics(tukey: float, marker_series: pd.Series) -> Tuple[float, float, float, float, float]:
    """Gets sample statistics"""  # TODO
    first_quartile, third_quartile = marker_series
    iqr = third_quartile - first_quartile
    upper_cutoff = third_quartile + (iqr * tukey)
    lower_cutoff = first_quartile - (iqr * tukey)
    return Stats(first_quartile, third_quartile, iqr, lower_cutoff, upper_cutoff)


def run_scouts(input_df: pd.DataFrame, sample_list: List[Tuple[str, str]], cutoff_df: pd.DataFrame, cutoff_rule: str,
               marker_rule: str, export_csv: bool, export_excel: bool, single_excel: bool, non_outliers: bool,
               bottom_outliers: bool, output_folder: str) -> None:
    """Runs SCOUTS"""  # TODO
    import time
    for data in yield_dataframes(input_df=input_df, sample_list=sample_list, cutoff_df=cutoff_df,
                                 cutoff_rule=cutoff_rule, marker_rule=marker_rule, non_outliers=non_outliers,
                                 bottom_outliers=bottom_outliers):
        print(data)
        print('next df ...')
        time.sleep(1)
    if export_csv:
        print('export_csv')
    if export_excel:
        print('export_excel')
    if single_excel:
        print('single_excel')


def yield_dataframes(input_df: pd.DataFrame, sample_list: List[Tuple[str, str]], cutoff_df: pd.DataFrame,
                     cutoff_rule: str, marker_rule: str, non_outliers: bool,
                     bottom_outliers: bool) -> Generator[pd.DataFrame, None, None]:
    """ Yields dataframes"""  # TODO
    if 'ref' in cutoff_rule:
        reference = get_reference_sample_name(sample_list)
        if 'any' in marker_rule:
            yield from scouts_by_reference_any_marker(input_df=input_df, cutoff_df=cutoff_df, reference=reference,
                                                      bottom_outliers=bottom_outliers, non_outliers=non_outliers)
        if 'single' in marker_rule:
            yield from scouts_by_reference_single_marker(input_df=input_df, cutoff_df=cutoff_df, reference=reference,
                                                         bottom_outliers=bottom_outliers, non_outliers=non_outliers)
    if 'sample' in cutoff_rule:
        samples = get_all_sample_names(sample_list)
        if 'any' in marker_rule:
            yield from scouts_by_sample_any_marker(input_df=input_df, cutoff_df=cutoff_df, samples=samples,
                                                   bottom_outliers=bottom_outliers, non_outliers=non_outliers)
        if 'single' in marker_rule:
            yield from scouts_by_sample_single_marker(input_df=input_df, cutoff_df=cutoff_df, samples=samples,
                                                      bottom_outliers=bottom_outliers, non_outliers=non_outliers)


def scouts_by_reference_any_marker(input_df: pd.DataFrame, cutoff_df: pd.DataFrame, reference: str,
                                   bottom_outliers: bool, non_outliers: bool) -> Generator[pd.DataFrame, None, None]:
    """scouts_by_reference_any_marker"""  # TODO
    upper_cutoffs = ['z'] + [stat.upper_cutoff for stat in cutoff_df.loc[reference]]
    lower_cutoffs = [''] + [stat.lower_cutoff for stat in cutoff_df.loc[reference]]
    yield input_df.loc[(input_df > upper_cutoffs).all(axis=1)]
    if bottom_outliers is True:
        yield input_df.loc[(input_df < lower_cutoffs).all(axis=1)]
    if non_outliers is True:
        yield input_df.loc[(input_df < upper_cutoffs).all(axis=1) & (input_df < lower_cutoffs).all(axis=1)]


def scouts_by_reference_single_marker(input_df: pd.DataFrame, cutoff_df: pd.DataFrame, reference: str,
                                      bottom_outliers: bool, non_outliers: bool) -> Generator[pd.DataFrame, None, None]:
    """scouts_by_reference_single_marker"""  # TODO
    markers = get_marker_names_from_df(df=input_df)
    for marker in markers:
        upper_cutoff = cutoff_df.loc[reference, marker].upper_cutoff
        lower_cutoff = cutoff_df.loc[reference, marker].lower_cutoff
        yield input_df.loc[input_df[marker] > upper_cutoff]
        if bottom_outliers is True:
            yield input_df.loc[input_df[marker] < lower_cutoff]
        if non_outliers is True:
            yield input_df.loc[(input_df[marker] < upper_cutoff) &
                               (input_df[marker] > lower_cutoff)]


def scouts_by_sample_any_marker(input_df: pd.DataFrame, cutoff_df: pd.DataFrame, samples: List[str],
                                bottom_outliers: bool, non_outliers: bool) -> Generator[pd.DataFrame, None, None]:
    """scouts_by_sample_any_marker"""  # TODO
    upper_dfs = []
    lower_dfs = []
    non_dfs = []
    for sample in samples:
        upper_cutoffs = ['z'] + [stat.upper_cutoff for stat in cutoff_df.loc[sample]]
        lower_cutoffs = [''] + [stat.lower_cutoff for stat in cutoff_df.loc[sample]]
        filtered_df = filter_df_by_sample_name(df=input_df, sample=sample)
        upper_dfs.append(filtered_df.loc[(filtered_df > upper_cutoffs).all(axis=1)])
        if bottom_outliers is True:
            lower_dfs.append(filtered_df.loc[(filtered_df < lower_cutoffs).all(axis=1)])
        if non_outliers is True:
            non_dfs.append(filtered_df.loc[(filtered_df < upper_cutoffs).all(axis=1) &
                                           (filtered_df < lower_cutoffs).all(axis=1)])
    yield pd.concat(upper_dfs)
    if bottom_outliers is True:
        yield pd.concat(lower_dfs)
    if non_outliers is True:
        yield pd.concat(non_dfs)


def scouts_by_sample_single_marker(input_df: pd.DataFrame, cutoff_df: pd.DataFrame, samples: List[str],
                                   bottom_outliers: bool, non_outliers: bool) -> Generator[pd.DataFrame, None, None]:
    """scouts_by_sample_single_marker"""  # TODO
    markers = get_marker_names_from_df(df=input_df)
    for marker in markers:
        upper_dfs = []
        lower_dfs = []
        non_dfs = []
        for sample in samples:
            upper_cutoff = cutoff_df.loc[sample, marker].upper_cutoff
            lower_cutoff = cutoff_df.loc[sample, marker].lower_cutoff
            filtered_df = filter_df_by_sample_name(df=input_df, sample=sample)
            upper_dfs.append(filtered_df.loc[filtered_df[marker] > upper_cutoff])
            if bottom_outliers is True:
                lower_dfs.append(filtered_df.loc[filtered_df[marker] < lower_cutoff])
            if non_outliers is True:
                non_dfs.append(filtered_df.loc[(filtered_df[marker] < upper_cutoff) &
                                               (filtered_df[marker] > lower_cutoff)])
        yield pd.concat(upper_dfs)
        if bottom_outliers is True:
            yield pd.concat(lower_dfs)
        if non_outliers is True:
            yield pd.concat(non_dfs)


def old_yield_dataframes(log, df, sample_dict, control, outliers, by_marker, bottom_outliers):
    """Deprecated"""
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


def old_get_inverse_df(full_df, partial_df):
    """Deprecated"""
    df_merge = full_df.merge(partial_df.drop_duplicates(), on=list(full_df), how='left', indicator=True)
    inverse_df = full_df[df_merge['_merge'] == 'left_only']
    return inverse_df
