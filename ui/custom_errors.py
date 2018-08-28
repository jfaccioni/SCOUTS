from ui import messages


class EmptySampleList(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        messages.empty_sample_list(*args)


class ControlNotFound(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        messages.control_not_found(*args)


class PandasInputError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        messages.pandas_input_error(*args)


class SampleNamingError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        messages.sample_naming_error(*args)
