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
--------

Launch FlexLogger and open a project

.. literalinclude:: ../examples/launch_application.py
   :language: python
   :linenos:

Start and stop a test

.. literalinclude:: ../examples/manage_test_session.py
   :language: python
   :linenos:

Configure logging

.. literalinclude:: ../examples/configure_logging_specification.py
   :language: python
   :linenos:

Get and set channel values

.. literalinclude:: ../examples/getting_and_setting_channel_values.py
   :language: python
   :linenos: