import os


def get_project_root():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


class NoIOPathError(Exception):
    def __init__(self):
        super().__init__()


class NoReferenceError(Exception):
    def __init__(self):
        super().__init__()


class NoSampleError(Exception):
    def __init__(self):
        super().__init__()


class PandasInputError(Exception):
    def __init__(self):
        super().__init__()


class SampleNamingError(Exception):
    def __init__(self):
        super().__init__()
