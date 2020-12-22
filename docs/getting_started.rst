.. _getting_started:

Getting Started
===============

1. Create an instance of the :class:`.Application` class.  There are two ways to do this:

  * To launch a new FlexLogger application, call :meth:`.Application.launch()`.
  * To connect to an already-running FlexLogger application, use the standard initializer
    :class:`.Application()`. Note that before connecting to an already running instance of FlexLogger,
    the Automation server preference must be enabled. You can enable this preference by opening the
    "File>>Preferences" menu item, and then enabling the "Automation server" preference in the "General" tab.

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

.. literalinclude:: ../examples/Basic/launch_application.py
   :language: python
   :linenos:

Connect to FlexLogger when it is already running

.. literalinclude:: ../examples/Basic/connect_to_application.py
   :language: python
   :linenos:

Test Session
------------

Start and stop a test

.. literalinclude:: ../examples/Basic/start_and_stop_test_session.py
   :language: python
   :linenos:

Adding a note to a log file

.. literalinclude:: ../examples/Basic/add_note.py
   :language: python
   :linenos:

Channels
--------

Getting the value of a channel

.. literalinclude:: ../examples/Basic/get_channel_value.py
   :language: python
   :linenos:

Setting the value of a channel

.. literalinclude:: ../examples/Basic/set_channel_value.py
   :language: python
   :linenos:

Logging
-------

Getting the log file base path and name

.. literalinclude:: ../examples/Basic/get_log_file_path_and_name.py
   :language: python
   :linenos:

Setting the log file base path and name

.. literalinclude:: ../examples/Basic/set_log_file_path_and_name.py
   :language: python
   :linenos:

Getting a test property

.. literalinclude:: ../examples/Basic/get_test_property.py
   :language: python
   :linenos:

Setting a test property

.. literalinclude:: ../examples/Basic/set_test_property.py
   :language: python
   :linenos:

Troubleshooting
===============

Can't connect to running FlexLogger
-----------------------------------
If you get an error connecting to an already running instance of FlexLogger, the Automation
server preference may not be enabled. You can enable this preference by opening the
"File>>Preferences" menu item, and then enabling the "Automation server"
preference in the "General" tab.

.. image:: preference_automation_server.png

Exception on first call into FlexLogger
---------------------------------------
If you see an exception on the first call into FlexLogger similar to::

  grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
        status = StatusCode.UNAVAILABLE
        details = "failed to connect to all addresses"
        debug_error_string = "{"created":"@1608052709.612000000","description":"Failed to pick subchannel","file":"src/core/ext/filters/client_channel/client_channel.cc","file_line":4143,"referenced_errors":[{"created":"@1608052633.077000000","description":"failed to connect to all addresses","file":"src/core/ext/filters/client_channel/lb_policy/pick_first/pick_first.cc","file_line":398,"grpc_status":14}]}"

the problem may be an HTTP proxy.  To test this, in your Python script add the following lines
before your FlexLogger API calls:

.. code-block:: python

   if os.environ.get('https_proxy'):
      del os.environ['https_proxy']
   if os.environ.get('http_proxy'):
      del os.environ['http_proxy']

If this fixes the problem, try configuring your proxy to not affect traffic to localhost.
See `this GitHub issue <https://github.com/ni/niflexlogger-automation-python/issues/13>`_
for an example.