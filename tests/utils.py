from pathlib import Path


def get_project_path(project_name: str) -> Path:
    """Gets the assets project path for the given project name (with no ".flxproj")"""
    return Path(__file__).parent / ("assets/%s/%s.flxproj" % (project_name, project_name))
