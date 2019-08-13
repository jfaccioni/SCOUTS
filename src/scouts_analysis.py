import os
from pprint import pprint

import numpy as np
import pandas as pd

# Pandas DataFrame options (this goes to logfile)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('expand_frame_repr', False)


def analyse(widget, input_file, output_folder, cutoff_rule, by_marker, tukey,
            export_csv, export_excel, group_excel, sample_list, gate_cutoff,
            not_outliers, bottom_outliers):
    df, control, samples = check_input(sample_list=sample_list,
                                       input_file=input_file, widget=widget)
    df = apply_ms_gate(df=df, gate_cutoff=gate_cutoff)
    # df.to_excel('gated_test.xlsx', index=False)
    sample_dict, marker_dict = get_cutoff_values(df=df, samples=samples,
                                                 gate_cutoff=gate_cutoff,
                                                 tukey=tukey)
    # Change directory to output directory, open log file
    os.chdir(output_folder)
    if 'log' not in os.listdir(os.getcwd()):
        os.mkdir('log')
    f = open(os.path.join('log', 'outlier_analysis_log.txt'), 'w')
    # Save all cutoff values as pretty-printed dictionary
    f.write('CUTOFF VALUES AS A DICTIONARY:\n')
    f.write('the data is ordered as:\n\n')
    f.write("{ 'sample' : { 'marker' : (. . .) } }\n")
    f.write("(. . .) represent this tuple: ")
    f.write("(Q1, Q3, IQR, (upper cutoff, lower cutoff)\n\n")
    pprint(sample_dict, stream=f, width=120)
    f.write('\n\n')
    # Iterate over yield_dataframes function, subsetting DataFrames and saving
    # each DataFrame to a different file
    df_list = []
    for dataframe, *names in yield_dataframes(log=f, df=df,
                                              sample_dict=sample_dict,
                                              control=control,
                                              outliers=cutoff_rule,
                                              by_marker=by_marker,
                                              bottom_outliers=bottom_outliers):
        m, s, n, c = names
        population_df = None
        if not_outliers:
            population_df = get_inverse_df(df, dataframe)
        # Create subfolder in output directory for each sample
        if s not in os.listdir(os.getcwd()):
            os.mkdir(s)
        main_name = f'{m}_{s}_{c}_cutoff_by_{n}'
        # avoids error when marker name has / or \ in it
        main_name = main_name.replace('\\', '_')
        main_name = main_name.replace('/', '_')
        output = os.path.join(s, f'{main_name}')
        if export_csv:
            dataframe.to_csv(f'{output}.csv', index=False)
            if population_df is not None:
                population_df.to_csv(f'{output}_pop.csv', index=False)
        if export_excel:
            dataframe.to_excel(f'{output}.xlsx', sheet_name=m, index=False)
            if population_df is not None:
                population_df.to_excel(f'{output}_pop.xlsx', sheet_name=m,
                                       index=False)
            if group_excel:
                df_list.append((dataframe, main_name))
                if population_df is not None:
                    df_list.append((population_df, main_name + '_pop'))

    # Close log file
    f.close()
    # Save master excel file
    if df_list:
        writer = pd.ExcelWriter('master_output.xlsx')
        for dataframe, name in df_list:
            dataframe.to_excel(writer, name, index=False)
        writer.save()


def check_input(sample_list, input_file, widget):
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
    return df, control, samples


def apply_ms_gate(df, gate_cutoff):
    if gate_cutoff is not None and type(gate_cutoff) != str:
        for index, row in df.iterrows():
            mean_row_value = np.mean(row[1:])
            if mean_row_value <= gate_cutoff:
                df = df.drop(index, axis=0)
        df.reset_index(drop=True, inplace=True)
    return df


def apply_rnaseq_gate(filtered_df, gate_cutoff):
    if type(gate_cutoff) == str:
        return filtered_df.replace(0, np.nan)


def get_cutoff_values(df, samples, gate_cutoff, tukey):
    # Build cutoff values
    marker_dict = {}
    sample_dict = {}  # Dict -> { 'sample' : { 'marker' : (. . .) } }
    for sample in samples:
        marker_dict = {}  # Dict -> { 'marker' : (Q1, Q3, IQR, cutoff value) }
        # Select rows containing the string stored in "sample"
        filtered_df = df[df[list(df)[0]].str.contains(sample)]  # don't ask!
        # apply gate -> sc-RNAseq rule
        rna_gated_df = apply_rnaseq_gate(filtered_df, gate_cutoff)
        if rna_gated_df is not None:
            filtered_df = rna_gated_df
        quantile_df = filtered_df.quantile([0.25, 0.75])
        for marker in quantile_df:
            first_quartile, third_quartile = quantile_df[marker]
            iqr = third_quartile - first_quartile
            upper_cutoff = third_quartile + (iqr * tukey)
            lower_cutoff = first_quartile - (iqr * tukey)
            cutoff = (upper_cutoff, lower_cutoff)
            marker_dict[marker] = (first_quartile, third_quartile, iqr, cutoff)
        sample_dict[sample] = marker_dict
    assert sample_dict, marker_dict
    return sample_dict, marker_dict


def yield_dataframes(log, df, sample_dict, control,
                     outliers, by_marker, bottom_outliers):

    # RULE: outliers by control cutoff, outliers for a single marker
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

    # RULE: outliers by control cutoff, outliers for any marker in row
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

    # RULE: outliers by sample cutoff, outliers for a single marker
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
    df_merge = full_df.merge(partial_df.drop_duplicates(), on=list(full_df),
                             how='left', indicator=True)
    inverse_df = full_df[df_merge['_merge'] == 'left_only']
    return inverse_df
