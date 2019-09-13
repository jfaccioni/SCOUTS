import unittest
from itertools import product
from unittest.mock import MagicMock, patch

from src.analysis import *


class TestSCOUTSAnalysis(unittest.TestCase):
    """Tests all functions (and other elements) from src.analysis module."""
    @classmethod
    def setUpClass(cls) -> None:
        """Loads data used for all unit tests."""
        # Test constants
        cls.samples = ['ct', 'treat', 'patient']
        cls.reference = 'ct'
        cls.sample_table_data = list(zip(cls.samples, ['yes', 'no', 'no']))
        cls.markers = ['Marker01', 'Marker02', 'Marker03', 'Marker04', 'Marker05']
        cls.tukey = 1.5
        # Test data from test-case.xlsx spreadsheet
        cls._backup_df = pd.read_excel('test-case.xlsx', sheet_name='raw data')
        cls.description_df = pd.read_excel('test-case.xlsx', sheet_name='raw data description',
                                           index_col=[0, 1])
        cls.cytof_df = pd.read_excel('test-case.xlsx', sheet_name='cytof gate 1.5').set_index('Sample')
        cls.cytof_description_df = pd.read_excel('test-case.xlsx', sheet_name='cytof gate 1.5 description',
                                                 index_col=[0, 1])
        cls.rnaseq_df = pd.read_excel('test-case.xlsx', sheet_name='rnaseq gate 2.0').set_index('Sample')
        cls.rnaseq_description_df = pd.read_excel('test-case.xlsx', sheet_name='rnaseq gate 2.0 description',
                                                  index_col=[0, 1])
        cls.output_cutoff_df = pd.read_excel('test-case.xlsx', sheet_name='raw data cutoff table').set_index('Sample')
        cls.quantiles_df = pd.read_excel('test-case.xlsx', sheet_name='quantiles', index_col=[0, 1])
        cls.outr_any_df = pd.read_excel('test-case.xlsx', sheet_name='OutR any', index_col=[0])
        cls.outr_mk2_df = pd.read_excel('test-case.xlsx', sheet_name='OutR Marker02', index_col=[0])
        cls.outs_any_df = pd.read_excel('test-case.xlsx', sheet_name='OutS any', index_col=[0])
        cls.outs_mk2_df = pd.read_excel('test-case.xlsx', sheet_name='OutS Marker02', index_col=[0])
        cls.stats_df = pd.read_excel('test-case.xlsx', sheet_name='raw data stats', index_col=[0, 1, 2])
        # Test data from internal functions
        cls.cutoff_df = cls.get_cutoff_df(cls.description_df)
        cls.cytof_cutoff_df = cls.get_cutoff_df(cls.cytof_description_df)
        cls.rnaseq_cutoff_df = cls.get_cutoff_df(cls.rnaseq_description_df)
        cls.reference_cutoff_df = cls.cutoff_df.loc[[cls.reference]]

    @classmethod
    def get_cutoff_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Used internally for construction of cutoff df, which contains Stats instances."""
        cutoff_df = pd.DataFrame(columns=cls.markers, index=cls.samples)
        for sample in cls.samples:
            for marker in cls.markers:
                cutoff_df.loc[sample, marker] = cls.build_stats(df=df, sample=sample, marker=marker)
        return cutoff_df

    @staticmethod
    def build_stats(df: pd.DataFrame, sample: str, marker: str) -> Stats:
        """Used internally for easy construction of Stats instances, based on raw data description excel spreadsheet."""
        return Stats(df.loc[sample].loc['Q1'][marker], df.loc[sample].loc['Q3'][marker],
                     df.loc[sample].loc['IQR'][marker], df.loc[sample].loc['Lower Tukey fence'][marker],
                     df.loc[sample].loc['Upper Tukey fence'][marker])

    def setUp(self) -> None:
        """Refreshes self.raw_df and self.indexed_df between tests, so that their values remain the same
        for all tests."""
        self.raw_df = self._backup_df.copy()
        self.indexed_df = self._backup_df.copy().set_index('Sample')

    def tearDown(self) -> None:
        """Deletes references to self.raw_df and self.indexed_df (just to be safe)."""
        del self.raw_df
        del self.indexed_df

    def test_namedtuple_stats(self) -> None:
        attrs = ['first_quartile', 'third_quartile', 'iqr', 'lower_cutoff', 'upper_cutoff']
        values = [1, 2, 3, 4, 5]
        stats = Stats(*values)
        for attr, value in zip(attrs, values):
            self.assertTrue(hasattr(stats, attr))
            self.assertEqual(getattr(stats, attr), value)

    def test_namedtuple_info(self) -> None:
        attrs = ['cutoff_from', 'reference', 'outliers_for', 'category']
        values = [1, 2, 3, 4]
        info = Info(*values)
        for attr, value in zip(attrs, values):
            self.assertTrue(hasattr(info, attr))
            self.assertEqual(getattr(info, attr), value)

    @patch('src.analysis.run_scouts')
    def test_function_start_scouts_marker_and_cutoff_rules(self, mock_run_scouts: MagicMock) -> None:
        start_scouts_kwargs = {
            'widget': 'QMainWindow',
            'input_file': 'test-case.xlsx',
            'output_folder': '.',
            'cutoff_rule': 'INPUT_VALUE',
            'marker_rule': 'INPUT_VALUE',
            'tukey_factor': 1.5,
            'export_csv': False,
            'export_excel': False,
            'single_excel': False,
            'sample_list': self.sample_table_data,
            'gating': 'no_gate',
            'gate_cutoff_value': None,
            'export_gated': False,
            'non_outliers': False,
            'bottom_outliers': False
        }
        expected_kwargs = {
            'widget': 'QMainWindow',
            'df': self.indexed_df,
            'cutoff_df': 'TEST_CASE',
            'samples': self.samples,
            'markers': self.markers,
            'reference': 'TEST_CASE',
            'cutoff_rule': 'TEST_CASE',
            'marker_rule': 'TEST_CASE',
            'export_csv': False,
            'export_excel': False,
            'single_excel': False,
            'export_gated': False,
            'non_outliers': False,
            'bottom_outliers': False,
            'output_folder': '.'
        }
        for marker_rule, cutoff_rule in product(['any', 'single', 'any single'], ['ref', 'sample', 'ref sample']):
            # Set input values
            start_scouts_kwargs['cutoff_rule'] = cutoff_rule
            start_scouts_kwargs['marker_rule'] = marker_rule
            # Fetch expected values
            expected_kwargs['cutoff_rule'] = cutoff_rule
            expected_kwargs['marker_rule'] = marker_rule
            if 'ref' in cutoff_rule:
                expected_kwargs['reference'] = self.reference
                if cutoff_rule == 'ref':
                    expected_kwargs['cutoff_df'] = self.reference_cutoff_df
                else:
                    expected_kwargs['cutoff_df'] = self.cutoff_df
            else:
                expected_kwargs['reference'] = None
                expected_kwargs['cutoff_df'] = self.cutoff_df
            # Run tests
            start_scouts(**start_scouts_kwargs)
            self.start_scouts_kwargs_test(expected_kwargs=expected_kwargs, actual_kwargs=mock_run_scouts.call_args[1])

    @patch('src.analysis.run_scouts')
    def test_function_start_scouts_gating_rules(self, mock_run_scouts: MagicMock) -> None:
        start_scouts_kwargs = {
            'widget': 'QMainWindow',
            'input_file': 'test-case.xlsx',
            'output_folder': '.',
            'cutoff_rule': 'sample',
            'marker_rule': 'single',
            'tukey_factor': 1.5,
            'export_csv': False,
            'export_excel': False,
            'single_excel': False,
            'sample_list': self.sample_table_data,
            'gating': 'INPUT_VALUE',
            'gate_cutoff_value': 'INPUT_VALUE',
            'export_gated': False,
            'non_outliers': False,
            'bottom_outliers': False}
        expected_kwargs = {
            'widget': 'QMainWindow',
            'df': 'TEST_CASE',
            'cutoff_df': 'TEST_CASE',
            'samples': self.samples,
            'markers': self.markers,
            'reference': None,
            'cutoff_rule': 'sample',
            'marker_rule': 'single',
            'export_csv': False,
            'export_excel': False,
            'single_excel': False,
            'export_gated': False,
            'non_outliers': False,
            'bottom_outliers': False,
            'output_folder': '.'
        }
        for gating_rule, gating_value in {'no_gate': None, 'cytof': 1.5, 'rnaseq': 2.0}.items():
            # Set input values
            start_scouts_kwargs['gating'] = gating_rule
            start_scouts_kwargs['gate_cutoff_value'] = gating_value
            # Fetch expected values
            if gating_rule == 'no_gate':
                expected_kwargs['df'] = self.indexed_df
                expected_kwargs['cutoff_df'] = self.cutoff_df
            elif gating_rule == 'cytof':
                expected_kwargs['df'] = self.cytof_df
                expected_kwargs['cutoff_df'] = self.cytof_cutoff_df
            elif gating_rule == 'rnaseq':
                expected_kwargs['df'] = self.rnaseq_df
                expected_kwargs['cutoff_df'] = self.rnaseq_cutoff_df
            start_scouts(**start_scouts_kwargs)
            self.start_scouts_kwargs_test(expected_kwargs=expected_kwargs, actual_kwargs=mock_run_scouts.call_args[1])

    def start_scouts_kwargs_test(self, expected_kwargs: Dict, actual_kwargs: Dict) -> None:
        """Helper function for testing call values on start_scouts function."""
        for expected_arg, actual_arg in zip(expected_kwargs.values(), actual_kwargs.values()):
            if isinstance(expected_arg, pd.DataFrame):
                pd.testing.assert_frame_equal(expected_arg, actual_arg, check_dtype=False)
            else:
                self.assertEqual(expected_arg, actual_arg)

    def test_function_load_dataframe(self) -> None:
        pd.testing.assert_frame_equal(self.raw_df, load_dataframe('test-case.xlsx'), check_dtype=False)
        pd.testing.assert_frame_equal(self.raw_df, load_dataframe('test-case.csv'), check_dtype=False)
        with self.assertRaises(FileNotFoundError):
            load_dataframe('this-file-does-not-exist.xlsx')
        with self.assertRaises(PandasInputError):
            load_dataframe('test-case.wrong_extension')

    def test_function_get_marker_names(self) -> None:
        marker_names = get_marker_names(df=self.indexed_df)
        self.assertEqual(marker_names, self.markers)

    def test_function_get_all_sample_names(self) -> None:
        sample_names = get_all_sample_names(self.sample_table_data)
        self.assertEqual(sample_names, self.samples)

    def test_function_validate_sample_names(self) -> None:
        validate_sample_names(samples=self.samples, df=self.indexed_df)
        invalid_samples = ['what', 'are', 'these?']
        with self.assertRaises(SampleNamingError):
            validate_sample_names(samples=invalid_samples, df=self.indexed_df)
        for bad_sample in invalid_samples:
            with self.assertRaises(SampleNamingError):
                validate_sample_names(samples=[bad_sample], df=self.indexed_df)

    def test_function_get_reference_sample_name(self) -> None:
        reference_name = get_reference_sample_name(self.sample_table_data)
        self.assertEqual(reference_name, self.reference)

    def test_function_apply_cytof_gating(self) -> None:
        apply_cytof_gating(df=self.indexed_df, cutoff=1.5)
        pd.testing.assert_frame_equal(self.indexed_df, self.cytof_df, check_dtype=False)

    def test_function_apply_rnaseq_gating(self) -> None:
        apply_rnaseq_gating(df=self.indexed_df, cutoff=2.0)
        pd.testing.assert_frame_equal(self.indexed_df, self.rnaseq_df, check_dtype=False)

    def test_function_get_cutoff_dataframe(self) -> None:
        cutoff = get_cutoff_dataframe(df=self.indexed_df, samples=self.samples, markers=self.markers,
                                      reference=None, cutoff_rule='sample', tukey=1.5)
        pd.testing.assert_frame_equal(cutoff, self.cutoff_df, check_dtype=False)
        cutoff = get_cutoff_dataframe(df=self.indexed_df, samples=self.samples, markers=self.markers,
                                      reference=self.reference, cutoff_rule='ref', tukey=1.5)
        pd.testing.assert_frame_equal(cutoff, self.reference_cutoff_df, check_dtype=False)
        cutoff = get_cutoff_dataframe(df=self.indexed_df, samples=self.samples, markers=self.markers,
                                      reference=self.reference, cutoff_rule='ref sample', tukey=1.5)
        pd.testing.assert_frame_equal(cutoff, self.cutoff_df, check_dtype=False)

    def test_function_get_cutoff(self) -> None:
        cutoff = get_cutoff(df=self.indexed_df, samples=self.samples, markers=self.markers, tukey=self.tukey)
        pd.testing.assert_frame_equal(cutoff, self.cutoff_df, check_dtype=False)
        cutoff = get_cutoff(df=self.indexed_df, samples=[self.reference], markers=self.markers, tukey=self.tukey)
        pd.testing.assert_frame_equal(cutoff, self.reference_cutoff_df, check_dtype=False)

    def test_function_get_sample_cutoff(self) -> None:
        for sample in self.samples:
            sample_cutoff = get_sample_cutoff(df=self.indexed_df, sample=sample, tukey=self.tukey)
            for index, marker in enumerate(self.markers):
                stats_instance = sample_cutoff[index]
                self.assertEqual(stats_instance, self.cutoff_df.loc[sample, marker])

    def test_function_filter_df_by_sample_in_index(self) -> None:
        for sample in self.samples:
            filtered_df = filter_df_by_sample_in_index(df=self.indexed_df, sample=sample)
            self.assertTrue(all(sample in i for i in filtered_df.index))
            for other_sample_name in [s for s in self.samples if s != sample]:
                self.assertFalse(any(other_sample_name in i for i in filtered_df.index))

    def test_function_get_marker_statistics(self) -> None:
        for sample in self.samples:
            for marker in self.markers:
                marker_series = self.quantiles_df.loc[sample, marker]
                stats = get_marker_statistics(tukey=self.tukey, marker_series=marker_series)
                self.assertEqual(stats.lower_cutoff, self.description_df.loc[sample].loc['Lower Tukey fence', marker])
                self.assertEqual(stats.upper_cutoff, self.description_df.loc[sample].loc['Upper Tukey fence', marker])

    def test_function_run_scouts(self) -> None:
        # TODO: how to test this? (central function)
        pass

    def test_function_create_stats_dfs(self) -> None:
        # OutS any marker, no bottom, no non
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='sample', marker_rule='any',
                                   samples=self.samples, bottom=False, non=False)
        self.assertTrue('OutS any marker' in df_dict)
        self.assertTrue(all(sheetname not in df_dict for sheetname in ['OutS single marker',
                                                                       'OutR any marker',
                                                                       'OutR single marker']))
        self.assertEqual(len(df_dict['OutS any marker']), 2 * len(self.samples) * 4)
        # OutS single marker, with bottom, no non
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='sample', marker_rule='single',
                                   samples=self.samples, bottom=True, non=False)
        self.assertTrue('OutS single marker' in df_dict)
        self.assertTrue(all(sheetname not in df_dict for sheetname in ['OutS any marker',
                                                                       'OutR any marker',
                                                                       'OutR single marker']))
        self.assertEqual(len(df_dict['OutS single marker']), 3 * len(self.samples) * 4)
        # OutR single marker, no bottom, with non
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='ref', marker_rule='any',
                                   samples=self.samples, bottom=False, non=True)
        self.assertTrue('OutR any marker' in df_dict)
        self.assertTrue(all(sheetname not in df_dict for sheetname in ['OutS any marker',
                                                                       'OutS single marker',
                                                                       'OutR single marker']))
        self.assertEqual(len(df_dict['OutR any marker']), 3 * len(self.samples) * 4)
        # OutR single marker, with bottom, with non
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='ref', marker_rule='single',
                                   samples=self.samples, bottom=True, non=True)
        self.assertTrue('OutR single marker' in df_dict)
        self.assertTrue(all(sheetname not in df_dict for sheetname in ['OutS any marker',
                                                                       'OutS single marker',
                                                                       'OutR any marker']))
        self.assertEqual(len(df_dict['OutR single marker']), 4 * len(self.samples) * 4)

    def test_function_add_whole_population_to_stats_dfs(self) -> None:
        # OutS any marker, no bottom, no non
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='sample', marker_rule='any',
                                   samples=self.samples, bottom=True, non=False)
        for sample in self.samples:
            self.assertTrue(df.loc[sample].loc['whole population'].isnull().all() for df in df_dict.values())
        add_whole_population_to_stats_dfs(input_df=self.indexed_df, stats_df_dict=df_dict, samples=self.samples)
        for sample in self.samples:
            self.assertTrue(not df.loc[sample].loc['whole population'].isnull().all() for df in df_dict.values())

    @patch('src.analysis.scouts_by_sample_single_marker')
    @patch('src.analysis.scouts_by_sample_any_marker')
    @patch('src.analysis.scouts_by_reference_single_marker')
    @patch('src.analysis.scouts_by_reference_any_marker')
    def test_function_yield_dataframes(self, mock_outr_any: MagicMock, mock_outr_single: MagicMock,
                                       mock_outs_any: MagicMock, mock_outs_single: MagicMock) -> None:
        mocks = (mock_outr_any, mock_outr_single, mock_outs_any, mock_outs_single)
        kwargs = {'input_df': '_', 'samples': '_', 'markers': '_', 'reference': '_', 'cutoff_df': '_',
                  'cutoff_rule': 'TEST_CASE', 'marker_rule': 'TEST_CASE', 'non_outliers': '_', 'bottom_outliers': '_'}
        list(yield_dataframes(**kwargs))
        for mock in mocks:
            mock.assert_not_called()
        kwargs['cutoff_rule'] = 'ref'
        kwargs['marker_rule'] = 'any'
        list(yield_dataframes(**kwargs))
        mock_outr_any.assert_called_once()
        kwargs['marker_rule'] = 'single'
        list(yield_dataframes(**kwargs))
        mock_outr_single.assert_called_once()
        kwargs['cutoff_rule'] = 'sample'
        kwargs['marker_rule'] = 'any'
        list(yield_dataframes(**kwargs))
        mock_outs_any.assert_called_once()
        kwargs['cutoff_rule'] = 'sample'
        kwargs['marker_rule'] = 'single'
        list(yield_dataframes(**kwargs))
        mock_outs_single.assert_called_once()
        for mock in mocks:
            mock.assert_called_once()

    def test_function_scouts_by_reference_any_marker(self) -> None:
        result = list(scouts_by_reference_any_marker(input_df=self.indexed_df, cutoff_df=self.cutoff_df,
                                                     reference=self.reference, bottom_outliers=False,
                                                     non_outliers=False))
        self.assertEqual(len(result), 1)
        df, info = result[0]
        pd.testing.assert_frame_equal(self.outr_any_df, df)
        self.assertEqual(info, Info(cutoff_from='reference', reference=self.reference, outliers_for='any marker',
                                    category='top outliers'))

    def test_function_scouts_by_reference_single_marker(self) -> None:
        result = list(scouts_by_reference_single_marker(input_df=self.indexed_df, cutoff_df=self.cutoff_df,
                                                        markers=['Marker02'], reference=self.reference,
                                                        bottom_outliers=False, non_outliers=False))
        self.assertEqual(len(result), 1)
        df, info = result[0]
        pd.testing.assert_frame_equal(self.outr_mk2_df, df)
        self.assertEqual(info, Info(cutoff_from='reference', reference=self.reference, outliers_for='Marker02',
                                    category='top outliers'))

    def test_function_scouts_by_sample_any_marker(self) -> None:
        result = list(scouts_by_sample_any_marker(input_df=self.indexed_df, cutoff_df=self.cutoff_df,
                                                  samples=self.samples, bottom_outliers=False, non_outliers=False))
        self.assertEqual(len(result), 1)
        df, info = result[0]
        pd.testing.assert_frame_equal(self.outs_any_df, df)
        self.assertEqual(info, Info(cutoff_from='sample', reference='n/a', outliers_for='any marker',
                                    category='top outliers'))

    def test_function_scouts_by_sample_single_marker(self) -> None:
        result = list(scouts_by_sample_single_marker(input_df=self.indexed_df, cutoff_df=self.cutoff_df,
                                                     samples=self.samples, markers=['Marker02'], bottom_outliers=False,
                                                     non_outliers=False))
        self.assertEqual(len(result), 1)
        df, info = result[0]
        pd.testing.assert_frame_equal(self.outs_mk2_df, df)
        self.assertEqual(info, Info(cutoff_from='sample', reference='n/a', outliers_for='Marker02',
                                    category='top outliers'))

    def test_function_add_scouts_data_to_summary(self) -> None:
        columns = ['file number'] + list(Info._fields)
        df = pd.DataFrame(columns=columns)
        self.assertTrue(df.empty)
        info = Info(cutoff_from='sample', reference='n/a', outliers_for='Marker02', category='top outliers')
        df = add_scouts_data_to_summary(df=df, i=1, info=info)
        self.assertTrue(len(df), 1)
        pd.testing.assert_series_equal(df.iloc[0], pd.Series([1, 'sample', 'n/a', 'Marker02', 'top outliers'],
                                                             index=columns), check_names=False)
        for i in range(2, 5):
            df = add_scouts_data_to_summary(df=df, i=i, info=info)
            self.assertTrue(len(df), i)

    def test_function_add_scouts_data_to_stats(self) -> None:
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='sample', marker_rule='single',
                                   samples=self.samples, bottom=False, non=False)
        data, info = list(scouts_by_sample_single_marker(input_df=self.indexed_df, cutoff_df=self.cutoff_df,
                                                         samples=self.samples, markers=['Marker02'],
                                                         bottom_outliers=False, non_outliers=False))[0]
        add_scouts_data_to_stats(data=data, samples=self.samples, stats_df_dict=df_dict, info=info)
        df = df_dict['OutS single marker']
        for sample in self.samples:
            values = get_values_df_or_series(data, sample, info)
            pd.testing.assert_series_equal(df.loc[(sample, info.category), info.outliers_for], values,
                                           check_dtype=False)
            pd.testing.assert_series_equal(self.stats_df.loc[(sample, info.category), info.outliers_for], values,
                                           check_dtype=False)

    def test_function_get_values_df(self) -> None:
        data, info = list(scouts_by_sample_single_marker(input_df=self.indexed_df, cutoff_df=self.cutoff_df,
                                                         samples=self.samples, markers=['Marker02'],
                                                         bottom_outliers=False, non_outliers=False))[0]
        for sample in self.samples:
            values = get_values_df_or_series(data=data, sample=sample, info=info)
            pd.testing.assert_series_equal(self.stats_df.loc[(sample, info.category), info.outliers_for], values,
                                           check_dtype=False)

    def test_function_get_key_from_info(self) -> None:
        info = Info(cutoff_from='sample', reference='', outliers_for='any marker', category='')
        self.assertEqual('OutS any marker', get_key_from_info(info))
        info = Info(cutoff_from='sample', reference='', outliers_for='some other marker', category='')
        self.assertEqual('OutS single marker', get_key_from_info(info))
        info = Info(cutoff_from='reference', reference='', outliers_for='any marker', category='')
        self.assertEqual('OutR any marker', get_key_from_info(info))
        info = Info(cutoff_from='reference', reference='', outliers_for='some other marker', category='')
        self.assertEqual('OutR single marker', get_key_from_info(info))

    @patch('src.analysis.pd.DataFrame.to_excel')
    def test_function_generate_summary_table(self, mock_to_excel: MagicMock) -> None:
        path = 'some/path/to/file.xlsx'
        generate_summary_table(summary_df=self.indexed_df, summary_path=path)
        expected_args = [path]
        expected_kwargs = {'sheet_name': 'Summary', 'index': False}
        mock_to_excel.assert_called_with(*expected_args, **expected_kwargs)

    @patch('src.analysis.pd.DataFrame.to_excel')
    @patch('src.analysis.pd.ExcelWriter')
    def test_function_generate_stats_table(self, mock_excel_writer: MagicMock, mock_to_excel: MagicMock) -> None:
        df_dict = create_stats_dfs(markers=self.markers, cutoff_rule='sample', marker_rule='any', samples=self.samples,
                                   bottom=False, non=False)
        path = 'some/path/to/file.xlsx'
        sheet_name = list(df_dict.keys())[-1]
        generate_stats_table(stats_df_dict=df_dict, stats_path=path)
        mock_excel_writer.assert_called_with(path)
        mock_to_excel.assert_called_with(mock_excel_writer.return_value, sheet_name=sheet_name)
        mock_excel_writer.return_value.save.assert_called_once()

    @patch('src.analysis.pd.DataFrame.to_excel')
    def test_function_generate_cutoff_table(self, mock_to_excel: MagicMock) -> None:
        path = 'some/path/to/file.xlsx'
        generate_cutoff_table(cutoff_df=self.cutoff_df, cutoff_path=path)
        expected_args = [path]
        expected_kwargs = {'sheet_name': 'Cutoff', 'index_label': 'Sample'}
        mock_to_excel.assert_called_with(*expected_args, **expected_kwargs)

    def test_function_get_output_cutoff_df(self) -> None:
        output_cutoff_df = get_output_cutoff_df(cutoff_df=self.cutoff_df, columns=self.output_cutoff_df.columns)
        pd.testing.assert_frame_equal(output_cutoff_df, self.output_cutoff_df, check_names=False, check_dtype=False)

    @patch('src.analysis.pd.DataFrame.to_excel')
    def test_function_generate_gated_table(self, mock_to_excel: MagicMock) -> None:
        path = 'some/path/to/file.xlsx'
        generate_gated_table(gated_df=self.indexed_df, gated_path=path)
        expected_args = [path]
        expected_kwargs = {'sheet_name': 'Gated Population', 'index': False}
        mock_to_excel.assert_called_with(*expected_args, **expected_kwargs)

    @patch('src.analysis.read_excel_data')
    def test_function_merge_excel_files(self, mock_read_excel_data: MagicMock) -> None:
        output_path = 'some/path/to/folder/subfolder'
        summary_path = 'some/path/to/summary.xlsx'
        excels = ['some.xlsx', 'excel.xslx', 'file.xlsx', 'names.xlsx']
        mock_sheet = [['A1', 'B1', 'C1'], ['A2', 'B2', 'C2']]
        mock_read_excel_data.return_value = mock_sheet
        wb = merge_excel_files(output_path=output_path, summary_path=summary_path, excels=excels)
        self.assertEqual(len(wb.sheetnames), len(excels) + 1)
        for sheet in wb.sheetnames:
            for row, mock_row in zip(wb[sheet].iter_rows(), mock_sheet):
                for cell, mock_cell_value in zip(row, mock_row):
                    self.assertEqual(cell.value, mock_cell_value)

    @patch('src.analysis.load_workbook')
    def test_function_read_excel_data(self, mock_load_workbook: MagicMock) -> None:
        path = 'some/path/to/file.xlsx'
        wb = Workbook()
        ws = wb.active
        ws.cell(row=1, column=1, value='a')
        ws.cell(row=1, column=2, value='b')
        ws.cell(row=2, column=1, value='c')
        ws.cell(row=2, column=2, value='d')
        mock_load_workbook.return_value = wb
        result = read_excel_data(path=path)
        self.assertEqual(result, [['a', 'b'], ['c', 'd']])
        mock_load_workbook.assert_called_once_with(path)


if __name__ == '__main__':
    unittest.main()
