from contextlib import contextmanager
from pathlib import Path
from shutil import copy, rmtree
from tempfile import TemporaryDirectory
from typing import Iterator

from flexlogger import Application, Project


def get_project_path(project_name: str) -> Path:
    """Get the assets project path for the given project name (with no ".flxproj").

    If you want to open the project, please use open_project() instead, as it will copy
    the project to a temporary directory and clean it up afterwards.
    """
    return Path(__file__).parent / ("assets/%s/%s.flxproj" % (project_name, project_name))


@contextmanager
def open_project(application: Application, project_name: str) -> Iterator[Project]:
    """Copy the project in assets with the given name to a temporary directory.

    This function returns a ContextManager, so it should be used in a `with` statement,
    and when it goes out of scope it will close the project and delete the temporary directory.
    """
    project_path = get_project_path(project_name)
    project_filename = project_path.name
    project_dir = project_path.parent

    tmp_directory = TemporaryDirectory(prefix="pyflextest_")
    source_files = project_dir.iterdir()
    for source_file in source_files:
        if source_file.is_file():
            copy(str(source_file), tmp_directory.name)
    project = application.open_project(Path(tmp_directory.name) / project_filename)
    try:
        yield project
    finally:
        project.close(allow_prompts=False)
        rmtree(tmp_directory.name)
