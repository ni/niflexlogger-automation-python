import fileinput
import re
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Pattern, Tuple

from grpc_tools import protoc

PROTO_PATHS = [
    "ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols",
    "DiagramSdk/Automation/DiagramSdk.Automation.Protocols",
]  # type: List[str]


def _main(*args: str) -> int:
    exit_code = call_protoc()
    if exit_code != 0:
        return exit_code
    move_files()
    fix_imports()
    return 0


def call_protoc() -> int:
    args = [
        "--proto_path=protobuf",
        "--python_out=flexlogger",
        "--grpc_python_out=flexlogger",
    ]
    args += ["--proto_path=protobuf/" + x for x in PROTO_PATHS]
    args += ["protobuf/" + x + "/*.proto" for x in PROTO_PATHS]

    return subprocess.run(["python", "-m", "grpc_tools.protoc"] + args).returncode


def move_files():
    for path_str in PROTO_PATHS:
        source_dir = Path(".") / "flexlogger" / path_str
        dest_dir = Path(".") / "flexlogger" / path_str.replace(".", "/")
        for source_path in source_dir.glob("*"):
            dest_path = dest_dir / source_path.name
            source_path.rename(dest_path)
        source_dir.rmdir()


# This is needed because protoc assumes the generated modules will be at the root level,
# and we put them under the "flexlogger" package.
def fix_imports():
    replacements = []
    for path_str in PROTO_PATHS:
        first_part_of_module_path = path_str.split("/")[0]
        moduleRe = re.compile("^from " + first_part_of_module_path)
        replacements.append((moduleRe, "from flexlogger." + first_part_of_module_path))
    for path_str in PROTO_PATHS:
        files_dir = Path(".") / "flexlogger" / path_str.replace(".", "/")
        for file_path in files_dir.glob("*"):
            for line in fileinput.input([str(file_path)], inplace=True):
                for entry in replacements:
                    line = entry[0].sub(entry[1], line)
                print(line, end="")


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
