from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    "python-dateutil",
    "aws_kinesis_agg",
]

setup(
    name="amazon_kinesis_utils",
    version="0.1.5",
    license="MIT",
    author="Tamirlan Torgayev",
    author_email="torgayev@me.com",
    description="amazon-kinesis-utils: a library of useful utilities for Amazon Kinesis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    zip_safe=True,
    url="https://amazon-kinesis-utils.readthedocs.io/en/latest/",
    project_urls={
        "Source Code": "https://github.com/baikonur-oss/amazon-kinesis-utils",
    },
    packages=find_packages(exclude=("test",)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
