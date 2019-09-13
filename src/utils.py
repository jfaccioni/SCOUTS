import os


def get_project_root():
    """Returns the root folder for this project."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


class NoIOPathError(Exception):
    """Exception raised when no input file/output folder is provided."""
    def __init__(self):
        super().__init__()


class NoReferenceError(Exception):
    """Exception raised when the user wants to use SCOUTS by reference, but no references are found."""
    def __init__(self):
        super().__init__()


class NoSampleError(Exception):
    """Exception raised when no samples are found in the sample table."""
    def __init__(self):
        super().__init__()


class PandasInputError(Exception):
    """Exception raised when pandas cannot read the input file."""
    def __init__(self):
        super().__init__()


class SampleNamingError(Exception):
    """Exception raised when samples cannot be found in the input file."""
    def __init__(self):
        super().__init__()
