import os
import signal
from contextlib import contextmanager
from pathlib import Path
from shutil import copy
from tempfile import TemporaryDirectory
from typing import Iterator, List, Tuple

import psutil  # type: ignore
from flexlogger.automation import Application, Project


def get_project_path(project_name: str) -> Path:
    """Get the assets project path for the given project name (with no ".flxproj").

    If you want to open the project, please use open_project() or copy_project() instead,
    as they will copy the project to a temporary directory and clean it up afterwards.
    """
    return Path(__file__).parent / ("assets/%s/%s.flxproj" % (project_name, project_name))


def kill_all_open_flexloggers() -> None:
    """Kill all open FlexLogger.exe processes.

    The application fixture in conftest.py does not get closed until all tests
    are run, which means tests that don't use the fixture will fail because we
    won't be able to launch a new Application.  So every test that doesn't use the
    fixture needs to call this method first.
    """
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"].lower() == "flexlogger.exe":
            _kill_proc_tree(proc.info["pid"])
    assert_no_flexloggers_running()


def assert_no_flexloggers_running() -> None:
    """Assert that no FlexLogger.exe processes are running."""
    assert not any_flexloggers_running()


def any_flexloggers_running() -> bool:
    """Returns whether any FlexLogger.exe processes are running."""
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"].lower() == "flexlogger.exe":
            return True
    return False


@contextmanager
def open_project(application: Application, project_name: str) -> Iterator[Project]:
    """Copy the project with name project_name in the assets directory to a temp directory and open it.

    This function returns a ContextManager, so it should be used in a `with` statement,
    and when it goes out of scope it will close the project and delete the temporary directory.
    """
    with copy_project(project_name) as project_path:
        project = application.open_project(project_path)
        try:
            yield project
        finally:
            project.close()


@contextmanager
def copy_project(project_name: str) -> Iterator[Path]:
    """Copy a project with name project_name from the assets directory to a temp directory.

    This function returns a ContextManager, so it should be used in a `with` statement,
    and when it goes out of scope it will delete the temporary directory.

    Returns:
        The new project's path.
    """
    project_path = get_project_path(project_name)
    project_filename = project_path.name
    project_dir = project_path.parent

    # This directory gets cleaned up by the pytest framework, and if
    # we try to clean it up ourselves we can get pytest warnings when
    # the framework fails to delete it.
    tmp_directory = TemporaryDirectory(prefix="pyflextest_")
    source_files = project_dir.iterdir()
    for source_file in source_files:
        if source_file.is_file():
            copy(str(source_file), tmp_directory.name)
    yield Path(tmp_directory.name) / project_filename


def _kill_proc_tree(
    pid: int, sig: int = signal.SIGTERM, include_parent: bool = True, timeout: float = None
) -> Tuple[List, List]:
    """Kill a process tree (including grandchildren).

    Uses signal "sig" and returns a (gone, still_alive) tuple.
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(children, timeout=timeout)
    return (gone, alive)
