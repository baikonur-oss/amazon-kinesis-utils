from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'boto3',
    'python-dateutil',
    'aws_kinesis_agg',
]

setup(
    name='kinesis_logging_utils',
    version='0.1.0',
    license='MIT',
    author='Tamirlan Torgayev',
    author_email='torgayev@me.com',
    description='Baikonur Kinesis Logging utilities for Python Lambdas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    zip_safe=True,
    url='https://github.com/baikonur-oss/kinesis-logging-utils',
    project_urls={
        'Source Code': 'https://github.com/baikonur-oss/kinesis-logging-utils',
    },
    packages=find_packages(exclude=('test',)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
