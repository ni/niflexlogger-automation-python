from grpc_tools import protoc
import subprocess

args = [
    "--proto_path=protobuf",
    "--proto_path=protobuf/ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols",
    "--proto_path=protobuf/DiagramSdk/Automation/DiagramSdk.Automation.Protocols",
    "--python_out=flexlogger",
    "--grpc_python_out=flexlogger",
    "protobuf/DiagramSdk/Automation/DiagramSdk.Automation.Protocols/Identifiers.proto",
    "protobuf/ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols/FlexLoggerApplication.proto",
    "protobuf/ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols/Project.proto",
]

subprocess.run(["python", "-m", "grpc_tools.protoc"] + args)
