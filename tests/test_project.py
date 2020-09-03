# import pytest  # type: ignore
from pathlib import Path

from flexlogger import Application


class TestProject:
    def test__launch_FlexLogger__open_default_project__project_contains_standard_four_documents(
        self,
    ) -> None:
        project_path = Path(__file__).parent / "assets/DefaultProject/DefaultProject.flxproj"
        with Application.launch() as app:
            project = None
            try:
                project = app.open_project(project_path)
                assert project is not None
                # TODO assert on all 4 document types
            finally:
                if project is not None:
                    project.close(allow_prompts=False)
