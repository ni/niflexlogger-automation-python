===========  ====================================================
Info         NI FlexLogger API for Python
Author       NI
===========  ====================================================

About
=====
The **niflexlogger-automation** package contains an API (Application Programming
Interface) and examples for using Python to automate `NI FlexLogger <https://ni.com/flexlogger>`_.
The automation API supports modifying the configuration of existing FlexLogger projects and
controlling the execution of FlexLogger test sessions.
The package is implemented in Python. NI created and supports this package.

Requirements
============
**niflexlogger-automation** has the following requirements:

* FlexLogger 2021 R1+
* CPython 3.6 - 3.9

.. _installation_section:

Installation
============
To install **niflexlogger-automation**, use one of the following methods:

* `pip <https://pypi.python.org/pypi/pip>`_::

   $ python -m pip install niflexlogger-automation

* **easy_install** from `setuptools <https://pypi.python.org/pypi/setuptools>`_::

   $ python -m easy_install niflexlogger-automation

* Download the project source and run::

   $ python setup.py install

.. _usage_section:

Usage
=====
Refer to the `documentation <https://niflexlogger-automation.readthedocs.io>`_
for detailed information on how to use **niflexlogger-automation**.

.. _tests_section:

Tests
=====
To run the tests, you must first configure FlexLogger to load the test
plugins that the test projects use.  To do this, copy ``tests/assets/pythonTests.config``
to ``%public%\Documents\National Instruments\FlexLogger\Plugins\IOPlugins``, and in that file
replace ``<path to git repo>`` with the path to the cloned repo.

After this is done, you can run the tests with `tox <https://pypi.org/project/tox/>`_.

.. _support_section:

Support / Feedback
==================
The **niflexlogger-automation** package is supported by NI. For support for
**niflexlogger-automation**, open a request through the NI support portal at
`ni.com <https://www.ni.com>`_.

Bugs / Feature Requests
=======================
To report a bug or submit a feature request, use the
`GitHub issues page <https://github.com/ni/niflexlogger-automation-python/issues>`_.

License
=======
**niflexlogger-automation** is licensed under an MIT-style license (see `LICENSE
<LICENSE>`_).  Other incorporated projects may be licensed under different
licenses. All licenses allow for non-commercial and commercial use.
