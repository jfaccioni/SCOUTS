import unittest

from src.analysis import *
from src.gui import *
from src.utils import *


class TestSCOUTSGui(unittest.TestCase):
    """Tests all methods (and other elements) from src.gui.SCOUTS class."""
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication(sys.argv)
        cls.gui = SCOUTS()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_special_method_init(self) -> None:
        pass

    def test_method_rlimit(self) -> None:
        pass

    def test_method_widget_hposition(self) -> None:
        pass

    def test_method_goto_main_page(self) -> None:
        pass

    def test_method_goto_samples_page(self) -> None:
        pass

    def test_method_goto_gates_page(self) -> None:
        pass

    def test_method_get_path(self) -> None:
        pass

    def test_method_enable_single_excel(self) -> None:
        pass

    def test_method_write_to_sample_table(self) -> None:
        pass

    def test_method_remove_from_sample_table(self) -> None:
        pass

    def test_method_prompt_clear_data(self) -> None:
        pass

    def test_method_activate_gate(self) -> None:
        pass

    def test_method_analyse(self) -> None:
        pass

    def test_method_parse_input(self) -> None:
        pass

    def test_method_yield_samples_from_table(self) -> None:
        pass

    def test_method_module_done(self) -> None:
        pass

    def test_method_memory_warning(self) -> None:
        pass

    def test_method_same_sample(self) -> None:
        pass

    def test_method_more_than_one_reference(self) -> None:
        pass

    def test_method_confirm_clear_data(self) -> None:
        pass

    def test_method_generic_error_message(self) -> None:
        pass

    def test_method_not_implemented_error_message(self) -> None:
        pass

    def test_method_debug(self) -> None:
        pass

    def test_method_get_help(self) -> None:
        pass

    def test_method_closeEvent(self) -> None:
        pass


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
        cls.backup_df = pd.read_excel('test-case.xlsx', sheet_name='raw data')
        cls.cytof_df = pd.read_excel('test-case.xlsx', sheet_name='cytof gate 1.5').set_index('Sample')
        cls.rnaseq_df = pd.read_excel('test-case.xlsx', sheet_name='rnaseq gate 2.0').set_index('Sample')
        cls.description_df = pd.read_excel('test-case.xlsx', sheet_name='raw data description', index_col=[0, 1])
        cls.cutoff_table_df = pd.read_excel('test-case.xlsx', sheet_name='cutoff table').set_index('Sample')
        cls.quantiles_df = pd.read_excel('test-case.xlsx', sheet_name='quantiles', index_col=[0, 1])
        # Test data with reorganized logic (pandas DataFrame with Stats instances in its cells)
        cls.cutoff_df = cls.get_cutoff_df()
        cls.reference_df = cls.cutoff_df.loc[[cls.reference]]

    # noinspection PyUnresolvedReferences
    @classmethod
    def get_cutoff_df(cls) -> pd.DataFrame:
        """Used internally for construction of cutoff df, which contains Stats instances."""
        cutoff_df = pd.DataFrame(columns=cls.markers, index=cls.samples)
        for sample in cls.samples:
            for marker in cls.markers:
                cutoff_df.loc[sample, marker] = cls.build_stats(df=cls.description_df, sample=sample, marker=marker)
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
        self.raw_df = self.backup_df.copy()
        self.indexed_df = self.backup_df.copy().set_index('Sample')

    def tearDown(self) -> None:
        del self.raw_df
        del self.indexed_df

    def test_namedtuple_stats(self) -> None:
        pass

    def test_namedtuple_info(self) -> None:
        pass

    def test_function_analyse(self) -> None:
        pass

    def test_function_load_dataframe(self) -> None:
        self.assertTrue(self.raw_df.equals(load_dataframe('test-case.xlsx')))
        self.assertTrue(self.raw_df.equals(load_dataframe('test-case.csv')))
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
        self.assertTrue(self.indexed_df.equals(self.cytof_df))

    def test_function_apply_rnaseq_gating(self) -> None:
        apply_rnaseq_gating(df=self.indexed_df, cutoff=2.0)
        self.assertTrue(self.indexed_df.equals(self.rnaseq_df))

    def test_function_get_cutoff_dataframe(self) -> None:
        cutoff = get_cutoff_dataframe(df=self.indexed_df, samples=self.samples, markers=self.markers,
                                      reference=None, cutoff_rule='sample', tukey=1.5)
        self.assertTrue(cutoff.equals(self.cutoff_df))
        cutoff = get_cutoff_dataframe(df=self.indexed_df, samples=self.samples, markers=self.markers,
                                      reference=self.reference, cutoff_rule='ref', tukey=1.5)
        self.assertTrue(cutoff.equals(self.reference_df))
        cutoff = get_cutoff_dataframe(df=self.indexed_df, samples=self.samples, markers=self.markers,
                                      reference=self.reference, cutoff_rule='ref sample', tukey=1.5)
        self.assertTrue(cutoff.equals(self.cutoff_df))

    def test_function_get_cutoff(self) -> None:
        cutoff = get_cutoff(df=self.indexed_df, samples=self.samples, markers=self.markers, tukey=self.tukey)
        self.assertTrue(cutoff.equals(self.cutoff_df))
        cutoff = get_cutoff(df=self.indexed_df, samples=[self.reference], markers=self.markers, tukey=self.tukey)
        self.assertTrue(cutoff.equals(self.reference_df))

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

    def test_function_create_stats_df(self) -> None:
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
