import os
from pprint import pprint

import numpy as np
import pandas as pd

from custom_errors import (ControlNotFound, EmptySampleList, PandasInputError,
                           SampleNamingError)

# Pandas DataFrame options (this goes to logfile)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('expand_frame_repr', False)


def analyse(widget, input_file, output_folder, cutoff_rule, by_marker, tukey,
            export_csv, export_excel, group_excel, sample_list, gate_cutoff):
    # Parse sample names and control sample
    samples = []
    control = ''
    for sample_type, sample in sample_list:
        if sample_type == 'Yes':
            control = sample
        samples.append(sample)
    # Check if samples were passed on the input table at all
    try:
        assert samples
    except AssertionError:
        raise EmptySampleList
    # Check if there is one sample passed as control
    try:
        assert control
    except AssertionError:
        raise ControlNotFound
    # Read input as pandas DataFrame, fails if file has unsupported extension
    if input_file.endswith('.xlsx') or input_file.endswith('xls'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        raise PandasInputError(widget)
    # Check if sample names are part of any string in first row
    for sample in samples:
        try:
            assert any(sample in text for text in list(df.iloc[:, 0]))
        except AssertionError:
            raise SampleNamingError(widget)
    # Apply gate -> Mass Cytometry rule
    if gate_cutoff is not None and type(gate_cutoff) != str:
        for index, row in df.iterrows():
            mean_row_value = np.mean(row[1:])
            if mean_row_value <= gate_cutoff:
                df = df.drop(index, axis=0)
        df.reset_index(drop=True, inplace=True)
    # Build cutoff values
    sample_dict = {}  # Dict -> { 'sample' : { 'marker' : (. . .) } }
    for sample in samples:
        marker_dict = {}  # Dict -> { 'marker' : (Q1, Q3, IQR, cutoff value) }
        # Select rows containing the string stored in "sample"
        filtered_df = df[df[list(df)[0]].str.contains(sample)]  # don't ask!
        # apply gate -> sc-RNAseq rule
        if type(gate_cutoff) == str:
            filtered_df = filtered_df.replace(0, np.nan)
        quantile_df = filtered_df.quantile([0.25, 0.75])
        for marker in quantile_df:
            first_quartile, third_quartile = quantile_df[marker]
            iqr = third_quartile - first_quartile
            cutoff = (iqr * tukey) + third_quartile
            marker_dict[marker] = (first_quartile, third_quartile, iqr, cutoff)
            sample_dict[sample] = marker_dict
        assert sample_dict, marker_dict
    # Change directory to output directory, open log file
    os.chdir(output_folder)
    if 'log' not in os.listdir(os.getcwd()):
        os.mkdir('log')
    f = open(os.path.join('log', 'outlier_analysis_log.txt'), 'w')
    # Save all cutoff values as pretty-printed dictionary
    f.write('CUTOFF VALUES AS A DICTIONARY:\n')
    f.write('the data is ordered as:\n\n')
    f.write("{ 'sample' : { 'marker' : (. . .) } }\n")
    f.write("(. . .) represent this tuple: (Q1, Q3, IQR, cutoff value)\n\n")
    pprint(sample_dict, stream=f, width=100)
    f.write('\n\n')
    # Iterate over yield_dataframes function, subsetting DataFrames and saving
    # each DataFrame to a different file
    df_list = []
    for dataframe, m, s, n in yield_dataframes(log=f, df=df,
                                               sample_dict=sample_dict,
                                               control=control,
                                               outliers=cutoff_rule,
                                               by_marker=by_marker):
        # Create subfolder in output directory for each sample
        if s not in os.listdir(os.getcwd()):
            os.mkdir(s)
        main_name = f'{m}_{s}_cutoff_by_{n}'
        # avoids error when marker name has / or \ in it
        main_name = main_name.replace('\\', '_')
        main_name = main_name.replace('/', '_')
        output = os.path.join(s, f'{main_name}')
        if export_csv:
            dataframe.to_csv(f'{output}.csv', index=False)
        if export_excel:
            dataframe.to_excel(f'{output}.xlsx', sheet_name=m, index=False)
            if group_excel:
                df_list.append((dataframe, main_name))
    # Close log file
    f.close()
    # Save master excel file
    if df_list:
        writer = pd.ExcelWriter('master_output.xlsx')
        for dataframe, name in df_list:
            dataframe.to_excel(writer, name, index=False)
        writer.save()


def yield_dataframes(log, df, sample_dict, control, outliers, by_marker):
    # RULE: outliers by control cutoff, outliers for a single marker
    if outliers in ('control', 'both') and by_marker in ('marker', 'both'):
        log.write('------- CUTOFF BY CONTROL, OUTLIERS BY MARKER -------\n\n\n')
        for sample, _ in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, cutoff) in sample_dict[control].items():
                output_df = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df.reset_index(drop=True, inplace=True)
                log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                log.write('METHOD: use control cutoff, ')
                log.write('check outliers for current marker only\n')
                log.write(f'CUTOFF: {cutoff}')
                log.write('\n\n')
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, marker, sample, 'control'
    # RULE: outliers by control cutoff, outliers for any marker in row
    if outliers in ('control', 'both') and by_marker in ('row', 'both'):
        log.write('------- CUTOFF BY CONTROL, OUTLIERS BY ROW -------\n\n\n')
        for sample, _ in sample_dict.items():
            log.write(f'SAMPLE: {sample}\n')
            log.write('METHOD: use control cutoff, ')
            log.write('check outliers for any markers in whole row')
            log.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            for marker, (*_, cutoff) in sample_dict[control].items():
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            output_df.reset_index(drop=True, inplace=True)
            log.write(str(output_df))
            log.write('\n\n\n\n')
            yield output_df, 'all_markers', sample, 'control'
    # RULE: outliers by sample cutoff, outliers for a single marker
    if outliers in ('sample', 'both') and by_marker in ('marker', 'both'):
        log.write('------- CUTOFF BY SAMPLE, OUTLIERS BY MARKER -------\n\n\n')
        for sample, mkdict in sample_dict.items():
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            for marker, (*_, cutoff) in mkdict.items():
                output_df = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df.reset_index(drop=True, inplace=True)
                log.write(f'MARKER: {marker}\nSAMPLE: {sample}\n')
                log.write('METHOD: use sample cutoff, ')
                log.write('check outliers for current marker only\n')
                log.write(f'CUTOFF: {cutoff}')
                log.write('\n\n')
                log.write(str(output_df))
                log.write('\n\n\n\n')
                yield output_df, marker, sample, 'sample'
    # RULE: outliers by sample cutoff, outliers for any marker in row
    if outliers in ('sample', 'both') and by_marker in ('row', 'both'):
        log.write('------- CUTOFF BY SAMPLE, OUTLIERS BY ROW -------\n\n\n')
        for sample, mkdict in sample_dict.items():
            log.write(f'SAMPLE: {sample}')
            log.write('METHOD: use sample cutoff, ')
            log.write('check outliers for any markers in whole row')
            log.write('\n\n')
            filtered_df = df[df[list(df)[0]].str.contains(sample)]
            output_df = pd.DataFrame(columns=list(df))
            for marker, (*_, cutoff) in mkdict.items():
                cutoff_rows = filtered_df.loc[filtered_df[marker] > cutoff]
                output_df = output_df.append(cutoff_rows, sort=False)
            output_df.drop_duplicates(inplace=True)
            output_df.reset_index(drop=True, inplace=True)
            log.write(str(output_df))
            log.write('\n\n\n\n')
            yield output_df, 'all_markers', sample, 'sample'
