import os


def get_project_root():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
