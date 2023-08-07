from pathlib import Path
from setuptools import setup, find_packages
from os import path

this_dir = path.abspath(path.dirname(__file__))

with open(path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def reqs(file_path):
    with open(Path(file_path)) as fh:
        return [
            r.strip()
            for r in fh.readlines()
            if not (r.startswith("#") or r.startswith("\n"))
        ]


aws_deps = ["smart_open[s3]"]
gcp_deps = ["smart_open[gcs]"]
azure_deps = ["smart_open[azure]", "azure-identity"]

setup(
    name="gretel-client",
    author="Gretel Labs, Inc.",
    author_email="open-source@gretel.ai",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Balance, anonymize, and share your data. With privacy guarantees.",
    url="https://github.com/gretelai/gretel-python-client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.9",
    entry_points={"console_scripts": ["gretel=gretel_client.cli.cli:cli"]},
    install_requires=reqs("requirements.txt"),
    tests_require=reqs("test-requirements.txt"),
    extras_require={
        "aws": aws_deps,
        "gcp": gcp_deps,
        "azure": azure_deps,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
