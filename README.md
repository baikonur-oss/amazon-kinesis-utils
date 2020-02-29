# kinesis-logging-utils
Baikonur Kinesis Logging utilities for Python Lambdas

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPi version](https://img.shields.io/pypi/v/kinesis-logging-utils.svg)](https://pypi.python.org/pypi/kinesis-logging-utils/) 
![](https://img.shields.io/badge/python-3.6+-blue.svg) 
![t](https://img.shields.io/badge/status-beta-orange.svg) 

## Module structure
- `kinesis`: Utilities to work with Kinesis Aggregated records, JSON events coming from CloudWatch Logs with 
subscription filters, gzipped JSON data and more.
- `s3`: Utilities to save string data to S3 easily.
- `baikonur_logging`: Utilities specific to Baikonur Kinesis/Lambda logging modules 
- `misc`: Various utilities useful when working with Kinesis Data Streams 

## Usage
```python
# import submodule you want to use with from import
from kinesis_logging_utils import kinesis

def lambda_handler(event, context):
    raw_records = event['Records']
    
    # kinesis.parse_json_logs parses aggregated/non-aggregated records, with or without gzip compression
    # non-JSON data is automatically rejected
    for payload in kinesis.parse_json_logs(raw_records):
        # kinesis.parse_json_logs is a generator, so we only have one payload in memory on every iteration
        print(f"Decoded payload: {payload}")
```

## Reference
See: https://kinesis-logging-utils.readthedocs.io/en/latest/

## Contributing

Make sure to have following tools installed:
- [pre-commit](https://pre-commit.com/)
- Sphinx for docs generation

### macOS
```console
$ brew install pre-commit

# set up pre-commit hooks by running below command in repository root
$ pre-commit install

# install sphinx
$ pip install sphinx
```
