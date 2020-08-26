import subprocess
import sys
from pathlib import Path

PROTO_PATHS = [
    "ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols",
    "DiagramSdk/Automation/DiagramSdk.Automation.Protocols",
]


def _main(*args: str) -> int:
    fixup_proto_files()
    exit_code = call_protoc()
    if exit_code != 0:
        return exit_code
    return 0


def fixup_proto_files() -> None:
    dest_dir = Path("./flexlogger/protobuf")
    dest_dir.mkdir(parents=True, exist_ok=True)

    for path_str in PROTO_PATHS:
        for proto_file in (Path("./protobuf") / path_str).glob("*.proto"):
            fixup_proto_file(proto_file, dest_dir / proto_file.name)


def fixup_proto_file(src: Path, dst: Path) -> None:
    contents = src.read_text()
    for proto_path in PROTO_PATHS:
        contents = contents.replace('import "' + proto_path + "/", 'import "')
    dst.write_text(contents)


def call_protoc() -> int:
    Path("./flexlogger/proto").mkdir(exist_ok=True)
    args = [
        "--proto_path=flexlogger/protobuf",
        "--python_out=flexlogger/proto",
        "--grpc_python_out=flexlogger/proto",
        "flexlogger/protobuf/*.proto",
    ]
    return subprocess.run([sys.executable, "-m", "grpc_tools.protoc"] + args).returncode


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
