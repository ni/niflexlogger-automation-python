import subprocess
import sys

from setuptools import find_packages, setup  # type: ignore
from setuptools.command.build_py import build_py as BuildPyCommand  # type: ignore
from setuptools.command.test import test as TestCommand  # type: ignore

pypi_name = "niflexlogger"

packages = find_packages(include=["flexlogger*"])


class GenerateProtobufAndBuildPyCommand(BuildPyCommand):
    def run(self):
        _generate_protobuf_classes()
        super().run()


def _generate_protobuf_classes():
    proc = subprocess.Popen(
        [sys.executable, "generate_protobuf_classes.py"],
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdout_text, stderr_text) = proc.communicate()
    if proc.returncode != 0:
        print("stdout: " + stdout_text)
        print("stderr: " + stderr_text)
        raise RuntimeError("generate_protobuf_classes returned error code %d" % proc.returncode)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest  # type: ignore

        pytest.main(self.test_args)


def _get_version(name):
    import os

    version = None
    script_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.join(script_dir, name)
    if not os.path.exists(os.path.join(script_dir, "VERSION")):
        version = "0.1.0"
    else:
        with open(os.path.join(script_dir, "VERSION"), "r") as version_file:
            version = version_file.read().rstrip()
    return version


def _read_contents(file_to_read):
    with open(file_to_read, "r") as f:
        return f.read()


setup(
    name=pypi_name,
    version=_get_version(pypi_name),
    description="NI FlexLogger Python API",
    long_description=_read_contents("README.rst"),
    author="National Instruments",
    maintainer="Ben Parrott, Greg Stoll",
    maintainer_email="ben.parrott@ni.com, greg.stoll@ni.com",
    keywords=["niflexlogger", "flexlogger"],
    license="MIT",
    packages=packages,
    scripts=["generate_protobuf_classes.py"],
    install_requires=["typing-extensions", "grpcio", "grpcio-tools", "pywin32"],
    setup_requires=["grpcio", "grpcio-tools"],
    tests_require=["pytest", "mypy", "npTDMS"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Hardware",
    ],
    cmdclass={"test": PyTest, "build_py": GenerateProtobufAndBuildPyCommand},
    package_data={"": ["VERSION", "*.pyi", "py.typed", "*.proto"]},
)
