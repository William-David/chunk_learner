from setuptools import setup, find_packages

setup(
    name="chunk-learner",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer[all]>=0.12.0",
    ],
    entry_points={
        "console_scripts": [
            "chunk-learner=chunk_learner.cli:app",
        ],
    },
    python_requires=">=3.14",
)
