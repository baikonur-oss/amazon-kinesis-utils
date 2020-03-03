# amazon-kinesis-utils
A library of useful utilities for Amazon Kinesis

![](https://img.shields.io/badge/python-3.6+-blue.svg) 
[![PyPi version](https://img.shields.io/pypi/v/amazon-kinesis-utils.svg)](https://pypi.python.org/pypi/amazon-kinesis-utils/) 
![t](https://img.shields.io/badge/status-beta-orange.svg) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/baikonur-oss/amazon-kinesis-utils.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/baikonur-oss/amazon-kinesis-utils/context:python)

[![CircleCI](https://circleci.com/gh/baikonur-oss/amazon-kinesis-utils.svg?style=svg)](https://circleci.com/gh/baikonur-oss/amazon-kinesis-utils)
[![codecov](https://codecov.io/gh/baikonur-oss/amazon-kinesis-utils/branch/master/graph/badge.svg)](https://codecov.io/gh/baikonur-oss/amazon-kinesis-utils)
[![Updates](https://pyup.io/repos/github/baikonur-oss/amazon-kinesis-utils/shield.svg)](https://pyup.io/repos/github/baikonur-oss/amazon-kinesis-utils/)
[![Documentation Status](https://readthedocs.org/projects/amazon-kinesis-utils/badge/?version=latest)](https://amazon-kinesis-utils.readthedocs.io/en/latest/?badge=latest)



## Reference
See: https://amazon-kinesis-utils.readthedocs.io/en/latest/

## Usage
```python
# import submodule you want to use with from import
from amazon_kinesis_utils import kinesis

def lambda_handler(event, context):
    raw_records = event['Records']
    
    # kinesis.parse_records parses aggregated/non-aggregated records, with or without gzip compression
    # it even unpacks CloudWatch Logs subscription filters messages
    for payload in kinesis.parse_records(raw_records):
        # kinesis.parse_records is a generator, so we only have one payload in memory on every iteration
        print(f"Decoded payload: {payload}")
```

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
$ pip install sphinx sphinx_rtd_theme
```
