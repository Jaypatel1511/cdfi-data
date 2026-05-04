from setuptools import setup, find_packages

setup(
    name="cdfidata",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.4.0",
        "numpy>=1.21.0",
        "requests>=2.27.0",
    ],
    extras_require={
        "parquet": ["pyarrow>=7.0.0"],
    },
)
