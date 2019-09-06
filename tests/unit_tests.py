from unittest.mock import patch
import unittest
from src.analysis import *
from itertools import product


class TestSCOUTSAnalysis(unittest.TestCase):
    """Tests all functions (and other elements) from src.analysis module."""
    @classmethod
    def setUpClass(cls) -> None:
        # Test constants
        cls.samples = ['ct', 'treat', 'patient']
        cls.reference = 'ct'
        cls.sample_table_data = list(zip(cls.samples, ['yes', 'no', 'no']))
        cls.markers = ['Marker01', 'Marker02', 'Marker03', 'Marker04', 'Marker05']
        cls.tukey = 1.5
        # Test data from spreadsheets
        cls._backup_df = pd.read_excel('test-case.xlsx', sheet_name='raw data')
        cls.description_df = pd.read_excel('test-case.xlsx', sheet_name='raw data description',
                                           index_col=[0, 1])
        cls.cytof_df = pd.read_excel('test-case.xlsx', sheet_name='cytof gate 1.5').set_index('Sample')
        cls.cytof_description_df = pd.read_excel('test-case.xlsx', sheet_name='cytof gate 1.5 description',
                                                 index_col=[0, 1])
        cls.rnaseq_df = pd.read_excel('test-case.xlsx', sheet_name='rnaseq gate 2.0').set_index('Sample')
        cls.rnaseq_description_df = pd.read_excel('test-case.xlsx', sheet_name='rnaseq gate 2.0 description',
                                                  index_col=[0, 1])
        cls.cutoff_table_df = pd.read_excel('test-case.xlsx', sheet_name='raw data cutoff table').set_index('Sample')
        cls.quantiles_df = pd.read_excel('test-case.xlsx', sheet_name='quantiles', index_col=[0, 1])
        cls.cutoff_df = cls.get_cutoff_df(cls.description_df)
        cls.cytof_cutoff_df = cls.get_cutoff_df(cls.cytof_description_df)
        cls.rnaseq_cutoff_df = cls.get_cutoff_df(cls.rnaseq_description_df)
        cls.reference_cutoff_df = cls.cutoff_df.loc[[cls.reference]]

    # noinspection PyUnresolvedReferences
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

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:
        self.raw_df = self._backup_df.copy()
        self.indexed_df = self._backup_df.copy().set_index('Sample')

    def tearDown(self) -> None:
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
    def test_function_start_scouts_marker_and_cutoff_rules(self, mock_run_scouts) -> None:
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
    def test_function_start_scouts_gating_rules(self, mock_run_scouts) -> None:
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
            with self.subTest(sample=sample):
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
        pass

    def test_function_create_stats_dfs(self) -> None:
        pass

    def test_function_yield_dataframes(self) -> None:
        pass

    def test_function_scouts_by_reference_any_marker(self) -> None:
        pass

    def test_function_scouts_by_reference_single_marker(self) -> None:
        pass

    def test_function_scouts_by_sample_any_marker(self) -> None:
        pass

    def test_function_scouts_by_sample_single_marker(self) -> None:
        pass

    def test_function_add_info_to_summary(self) -> None:
        pass

    def test_function_add_info_to_stats(self) -> None:
        pass

    def test_function_get_values_df(self) -> None:
        pass

    def test_function_get_key_from_info(self) -> None:
        pass

    def test_function_generate_summary_table(self) -> None:
        pass

    def test_function_generate_stats_table(self) -> None:
        pass

    def test_function_generate_cutoff_table(self) -> None:
        pass

    def test_function_merge_excel_files(self) -> None:
        pass

    def test_function_read_excel_data(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
