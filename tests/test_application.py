from flexlogger.automation import Application
import pytest  # type: ignore
import re


class TestApplication:
    @pytest.mark.integration  # type: ignore
    def test__launch_flexLogger__get_versions__versions_match_pattern(self, app: Application) -> None:
        version, version_string = app.get_version()

        version_pattern = re.compile(r"2\d.\d.\d.\d")
        assert version_pattern.match(version)
        version_string_pattern = re.compile(r"20\d\d Q\d")
        assert version_string_pattern.match(version_string)
