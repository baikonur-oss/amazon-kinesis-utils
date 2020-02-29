About Baikonur Kinesis/Lambda logging
=====================================

Baikonur Kinesis/Lambda logging requirements
--------------------------------------------

Baikonur Kinesis/Lambda logging can be defined as anything using Kinesis Data Streams with one or more of the
following Baikonur OSS Lambda Modules:

- terraform-aws-lambda-kinesis-forward_
- terraform-aws-lambda-kinesis-to-es_
- terraform-aws-lambda-kinesis-to-s3_

These modules have the following common schema requirements:

- All data must be JSON objects
- All data must include the following keys (key names are customizable for each Lambda module):

    - ``log_type``: Log type identifier
    - ``log_id``: Any unique identifier (e.g. ``uuid.uuid4()``)
    - ``time``: Any timestamp supported by dateutil.parser.parse_

Common schema requirements are derived from following needs:

1. Easier parsing
2. Interoperability between different Lambda modules

    - Different modules can be attached to a single Kinesis Data Stream
      and work on same data as long as data are JSON-objects and common schema requirements are met.

3. Ability to create behaviour based on keys in common schema

    - One of the most important features is ability to apply whitelist on ``log_type`` field to, for instance,
      ignore logs other than those specified.

``log_id`` and ``time`` keys are required by terraform-aws-lambda-kinesis-to-s3_ (to ensure unique filenames)
and terraform-aws-lambda-kinesis-to-es_ (for creating daily index names). Additionally, these fields are useful when
troubleshooting.

Nevertheless ``amazon-kinesis-utils`` module name and default field names in description above, usage of this module
and Lambda modules listed above are not limited to logging. As log as common schema requirements are met,

``amazon-kinesis-utils`` submodules with specifics
---------------------------------------------------

This module was originally created for Baikonur OSS Lambda modules for logging with Kinesis. However,
:ref:`api_ref_baikonur_logging` is the only submodule of ``amazon-kinesis-utils`` module that includes
implications specific to Lambda modules above and their prerequisites. Other submodules are made to be universal.


``baikonur_logging`` submodule specifics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Functions in :ref:`api_ref_baikonur_logging` submodule are provided to work with data structure called ``log_dict``.

``log_dict`` structure is as following:

>>> import datetime
>>> import uuid
>>> from kinesis_logging_utils import baikonur_logging
>>> log_dict = dict()
>>> baikonur_logging.append_to_log_dict(log_dict, log_type='test', log_data={'a':'b'}, log_timestamp=datetime.datetime.now().isoformat(), log_id=str(uuid.uuid4()))
>>> log_dict
{'test': {'records': [{'a': 'b'}], 'first_timestamp': datetime.datetime(2020, 3, 1, 4, 55, 24, 966601), 'first_id': '4604dea6-5439-427a-bb41-c2f4807f3b72'}

This data structure allows us to iterate on ``log_type`` and retrieve all logs for a ``log_type``.

``first_timestamp`` and ``first_id`` are mainly used to generate timestamped, unique filenames when saving logs to S3.


.. _dateutil.parser.parse: https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse
.. _terraform-aws-lambda-kinesis-forward: https://github.com/baikonur-oss/terraform-aws-lambda-kinesis-forward
.. _terraform-aws-lambda-kinesis-to-es: https://github.com/baikonur-oss/terraform-aws-lambda-kinesis-to-es
.. _terraform-aws-lambda-kinesis-to-s3: https://github.com/baikonur-oss/terraform-aws-lambda-kinesis-to-s3
