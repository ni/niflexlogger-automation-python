import subprocess
import sys
from itertools import chain
from pathlib import Path

PROTO_PATHS = [
    "ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols",
    "Core/Automation/Core.Automation.Protocols",
    "DiagramSdk/Automation/DiagramSdk.Automation.Protocols",
]

DEST_DIR = Path("./flexlogger/automation/proto")


def _main(*args: str) -> int:
    _prepare_dest_dir()
    _fixup_proto_files()
    exit_code = _call_protoc()
    if exit_code != 0:
        return exit_code
    _move_generated_files()
    return 0


def _prepare_dest_dir() -> None:
    for existing_generated_file in chain(DEST_DIR.glob("*_pb2.py"), DEST_DIR.glob("*_pb2_grpc.py")):
        existing_generated_file.unlink()


def _fixup_proto_files() -> None:
    for path_str in PROTO_PATHS:
        for proto_file in (Path("./protobuf") / path_str).glob("*.proto"):
            _fixup_proto_file(proto_file, DEST_DIR / proto_file.name)


def _fixup_proto_file(src: Path, dst: Path) -> None:
    contents = src.read_text()
    for proto_path in PROTO_PATHS:
        # We want the generated classes to import other generated classes with
        # something like
        #    from flexlogger.automation.proto import Identifiers
        # So we need the "import" statement in the .proto file to match this
        contents = contents.replace(
            'import "' + proto_path + "/", 'import "flexlogger/automation/proto/'
        )
    dst.write_text(contents)


def _move_generated_files() -> None:
    source_dir = DEST_DIR / "flexlogger/automation/proto"
    for source_path in source_dir.glob("*.py"):
        dest_path = DEST_DIR / source_path.name
        source_path.rename(dest_path)
    source_dir.rmdir()
    (DEST_DIR / "flexlogger/automation").rmdir()
    (DEST_DIR / "flexlogger").rmdir()


def _call_protoc() -> int:
    Path("./flexlogger/automation/proto").mkdir(exist_ok=True)
    args = [
        "--proto_path=.",
        "--python_out=flexlogger/automation/proto",
        "--grpc_python_out=flexlogger/automation/proto",
        "flexlogger/automation/proto/*.proto",
    ]
    return subprocess.run([sys.executable, "-m", "grpc_tools.protoc"] + args).returncode


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
