===========  ====================================================
Info         NI FlexLogger API for Python
Author       NI
===========  ====================================================

About
=====
The **niflexlogger-automation** package contains an API (Application Programming
Interface) and examples for using Python to automate `FlexLogger <https://ni.com/flexlogger>`_.
The automation API supports modifying the configuration of existing FlexLogger projects and
controlling the execution of FlexLogger tests.
The package is implemented in Python. NI created and supports this package.

Requirements
============
**niflexlogger-automation** has the following requirements:

* FlexLogger 2021 R3+
* CPython 3.6 - 3.9. If you do not have Python installed on your computer, go to python.org/downloads to download and install it.

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

Using the FlexLogger Python API
===============================
Refer to the `documentation <https://niflexlogger-automation.readthedocs.io/en/latest/getting_started.html>`_
for detailed information on how to use **niflexlogger-automation**.

Refer to `Getting Started with CompactDAQ and FlexLogger <https://learn.ni.com/learn/article/getting-started-with-compactdaq-and-flexlogger>`_, for more information on installing FlexLogger, using hardware, or downloading FlexLogger examples.

.. _tests_section:

Contribution to the FlexLogger Python API
=========================================
If you would like to contribute to this API, first validate your changes using the provided automated tests. The Python API package contains a number of automated tests which should be used to
validate API changes before submitting a pull request. If a pull request contains
new API functionality, new automated tests that exercise the new functionality
should be included with the pull request.

To run the automated tests for the Python API, you must first configure FlexLogger
to load the test plugins that the test projects use. To do this, copy
``tests/assets/pythonTests.config`` to 
``%public%\Documents\National Instruments\FlexLogger\Plugins\IOPlugins``, and in that
file replace ``<path to git repo>`` with the path to the cloned repo.

After this is done, you can run the tests with `tox <https://pypi.org/project/tox/>`_.

.. _support_section:

Support / Feedback
==================
The **niflexlogger-automation** package is supported by NI. For support for
**niflexlogger-automation**, open a request through the NI support portal at
`ni.com <https://www.ni.com>`_.

Bugs / Feature requests
=======================
To report a bug or submit a feature request, use the
`GitHub issues page <https://github.com/ni/niflexlogger-automation-python/issues>`_.

License
=======
**niflexlogger-automation** is licensed under an MIT-style license (see `LICENSE
<LICENSE>`_).  Other incorporated projects may be licensed under different
licenses. All licenses allow for non-commercial and commercial use.
