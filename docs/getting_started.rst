.. _getting_started:

Getting Started
===============

1. Create an instance of the :class:`.Application` class.  There are two ways to do this:

  * To launch a new FlexLogger application, call :meth:`.Application.launch()`.
  * To connect to an already-running FlexLogger application, use the standard initializer
    :class:`.Application()`.

2. Call :meth:`.Application.open_project()` to open a project.

After this, here's how to do several common tasks:

* **Start and stop a test**: The :attr:`.Project.test_session` property returns a
  :class:`.TestSession` object which has :meth:`~.TestSession.start()` and
  :meth:`~.TestSession.stop()` methods.

* **Configure test properties**: The :attr:`.Project.open_logging_specification_document()` method
  returns a :class:`.LoggingSpecificationDocument` object which has
  :meth:`~.LoggingSpecificationDocument.get_test_property()`,
  :meth:`~.LoggingSpecificationDocument.set_test_property()`, and
  :meth:`~.LoggingSpecificationDocument.remove_test_property()` methods.  The
  :meth:`~.LoggingSpecificationDocument.get_test_properties()` method returns the full
  :class:`.TestProperty` list for the project.

* **Configure the log file location**: The :attr:`.Project.open_logging_specification_document()` method
  returns a :class:`.LoggingSpecificationDocument` object which has
  :meth:`~.LoggingSpecificationDocument.set_log_file_base_path()` and
  :meth:`~.LoggingSpecificationDocument.set_log_file_name()` methods.

* **Read and write channel values**: Calling :meth:`.Project.open_channel_specification_document()`
  returns a :class:`.ChannelSpecificationDocument` object which has
  :meth:`~.ChannelSpecificationDocument.get_channel_value()` and 
  :meth:`~.ChannelSpecificationDocument.set_channel_value()` methods.

Examples
========

Communicating with FlexLogger
-----------------------------

Launch FlexLogger and open a project

.. literalinclude:: ../examples/basic/launch_application.py
   :language: python
   :linenos:

Connect to FlexLogger when it is already running

.. literalinclude:: ../examples/basic/connect_to_application.py
   :language: python
   :linenos:

Test Session
------------

Start and stop a test

.. literalinclude:: ../examples/basic/start_and_stop_test_session.py
   :language: python
   :linenos:

Adding a note to a log file

.. literalinclude:: ../examples/basic/add_note.py
   :language: python
   :linenos:

Channels
--------

Getting the value of a channel

.. literalinclude:: ../examples/basic/get_channel_value.py
   :language: python
   :linenos:

Setting the value of a channel

.. literalinclude:: ../examples/basic/set_channel_value.py
   :language: python
   :linenos:

Logging
-------

Getting the log file base path and name

.. literalinclude:: ../examples/basic/get_log_file_path_and_name.py
   :language: python
   :linenos:

Setting the log file base path and name

.. literalinclude:: ../examples/basic/set_log_file_path_and_name.py
   :language: python
   :linenos:

Getting a test property

.. literalinclude:: ../examples/basic/get_test_property.py
   :language: python
   :linenos:

Setting a test property

.. literalinclude:: ../examples/basic/set_test_property.py
   :language: python
   :linenos:
