import subprocess
import sys
from itertools import chain
from pathlib import Path
from platform import system
from shlex import quote

PROTO_PATHS = [
    "ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols",
    "Core/Automation/Core.Automation.Protocols",
    "DiagramSdk/Automation/DiagramSdk.Automation.Protocols",
]

RELATIVE_DEST_DIR = Path("./flexlogger/automation/proto")


def _has_src_dir() -> bool:
    return Path("./src/").exists()


def _get_dest_dir() -> Path:
    dest_dir = Path("./src" / RELATIVE_DEST_DIR)
    if dest_dir.exists():
        return dest_dir
    return RELATIVE_DEST_DIR


def _main(*args: str) -> int:
    _prepare_dest_dir()
    _fixup_proto_files()
    exit_code = _call_protoc()
    if exit_code != 0:
        return exit_code
    _move_generated_files()
    return 0


def _prepare_dest_dir() -> None:
    for existing_generated_file in chain(
        _get_dest_dir().glob("*_pb2.py"), _get_dest_dir().glob("*_pb2_grpc.py")
    ):
        existing_generated_file.unlink()


def _fixup_proto_files() -> None:
    for path_str in PROTO_PATHS:
        for proto_file in (Path("./protobuf") / path_str).glob("*.proto"):
            _fixup_proto_file(proto_file, _get_dest_dir() / proto_file.name)


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
    source_dir = _get_dest_dir() / "flexlogger/automation/proto"
    for source_path in source_dir.glob("*.py"):
        dest_path = _get_dest_dir() / source_path.name
        source_path.rename(dest_path)
    source_dir.rmdir()
    (_get_dest_dir() / "flexlogger/automation").rmdir()
    (_get_dest_dir() / "flexlogger").rmdir()


def _call_protoc() -> int:
    args = [
        "--proto_path=.",
        "--python_out=" + str(RELATIVE_DEST_DIR),
        "--grpc_python_out=" + str(RELATIVE_DEST_DIR),
        str(RELATIVE_DEST_DIR) + "/*.proto",
    ]

    cwd = "./src" if _has_src_dir() else None

    if system() == "Windows":
        return subprocess.run([sys.executable, "-m", "grpc_tools.protoc"] + args, cwd=cwd).returncode 
    else:
        # Need to run with shell=True so the .proto files will get
        # globbed on Linux.
        return subprocess.run(' '.join([quote(sys.executable), "-m", "grpc_tools.protoc"] + args), cwd=cwd, shell=True).returncode


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
