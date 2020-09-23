import os
import signal
from contextlib import contextmanager
from pathlib import Path
from shutil import copy, rmtree
from tempfile import TemporaryDirectory
from typing import Iterator, List, Tuple

import psutil  # type: ignore
from flexlogger.automation import Application, Project


def get_project_path(project_name: str) -> Path:
    """Get the assets project path for the given project name (with no ".flxproj").

    If you want to open the project, please use open_project() instead, as it will copy
    the project to a temporary directory and clean it up afterwards.
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
    for proc in psutil.process_iter(["pid", "name"]):
        assert proc.info["name"].lower() != "flexlogger.exe"


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
