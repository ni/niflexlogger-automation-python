.. _api_reference_page:

API Reference
==============

.. toctree::
   :maxdepth: 4
   :caption: Table of Contents


.. rubric:: Streaming channel data

FlexLogger streams channel data in two ways. You can run both at the same time.

* :meth:`.ChannelSpecificationDocument.stream_channel_data` streams data to plot, like the
  FlexLogger high speed graph. Each :class:`.StreamFrame` is a snapshot of the last seconds of
  every channel, reduced to minimum and maximum values so no peak is lost. Frames overlap, and
  FlexLogger skips frames when the client reads too slowly.
* :meth:`.ChannelSpecificationDocument.stream_raw_channel_data` streams every sample to analyze
  or record, exactly once and in time order, at the rate of each channel. Each
  :class:`.RawStreamFrame` holds the samples each channel acquired since the previous frame, as
  :class:`.ChannelSamples` made of :class:`.SampleSegment` runs. Frames never overlap and are
  never skipped. If the client reads so slowly that FlexLogger discards samples, the next
  segment reports :attr:`.SampleSegment.follows_gap`. Versions of FlexLogger that cannot stream
  raw channel data raise a :class:`.FlexLoggerError`.


.. automodule:: flexlogger.automation
   :members:
   :imported-members:


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`