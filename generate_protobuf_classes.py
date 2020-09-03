import subprocess
import sys
from pathlib import Path

PROTO_PATHS = [
    "ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols",
    "Core/Automation/Core.Automation.Protocols",
    "DiagramSdk/Automation/DiagramSdk.Automation.Protocols",
]


def _main(*args: str) -> int:
    _fixup_proto_files()
    exit_code = _call_protoc()
    if exit_code != 0:
        return exit_code
    _move_generated_files()
    _create_init_py()
    return 0


def _fixup_proto_files() -> None:
    dest_dir = Path("./flexlogger/proto")
    dest_dir.mkdir(parents=True, exist_ok=True)

    for path_str in PROTO_PATHS:
        for proto_file in (Path("./protobuf") / path_str).glob("*.proto"):
            _fixup_proto_file(proto_file, dest_dir / proto_file.name)


def _fixup_proto_file(src: Path, dst: Path) -> None:
    contents = src.read_text()
    for proto_path in PROTO_PATHS:
        # We want the generated classes to import other generated classes with
        # something like
        #    from flexlogger.proto import Identifiers
        # So we need the "import" statement in the .proto file to match this
        contents = contents.replace('import "' + proto_path + "/", 'import "flexlogger/proto/')
    dst.write_text(contents)


def _move_generated_files() -> None:
    dest_dir = Path("./flexlogger/proto")
    source_dir = dest_dir / "flexlogger/proto"
    for source_path in source_dir.glob("*.py"):
        dest_path = dest_dir / source_path.name
        source_path.rename(dest_path)
    source_dir.rmdir()
    (dest_dir / "flexlogger").rmdir()


def _create_init_py() -> None:
    dest_dir = Path("./flexlogger/proto")
    with open(str(dest_dir / "__init__.py"), "w") as f:
        f.write("# flake8: noqa")


def _call_protoc() -> int:
    Path("./flexlogger/proto").mkdir(exist_ok=True)
    args = [
        "--proto_path=.",
        "--python_out=flexlogger/proto",
        "--grpc_python_out=flexlogger/proto",
        "flexlogger/proto/*.proto",
    ]
    return subprocess.run([sys.executable, "-m", "grpc_tools.protoc"] + args).returncode


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
