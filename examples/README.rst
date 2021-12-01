===========  ====================================================
Info         NI FlexLogger Examples Readme
Author       NI
===========  ====================================================

About
=====
The Python automation API and examples enable you to modify existing FlexLogger projects and control the execution of FlexLogger test sessions.

The Python Examples folder includes the following types of examples:
* Basic: Demonstrate how to perform specific tasks.
* Test Sequencer: Demonstrate how to create basic test sequences that involve FlexLogger and hardware, such as DUTs and thermal chambers.
* Interactive: Demonstrate how to use the FlexLogger Python automation API to perform tasks interactively, depending on user input.

Requirements
============
* FlexLogger 2021 R3 or later
* Python 3.6-3.9
* pymodbus 2.5.3 (Only for the Thermal Chamber with Communication Protocol example)
* numpy 1.0 (Only for the Thermal Chamber with Communication Protocol example)

Folder Structure
================
Each FlexLogger Example folder contains the following components:
* Python Example (.py)
* Configuration file (.csv) (Only for Test Sequencer examples)
* Communication configuration file (.ini) (Only for the Thermal Chamber with Communication Protocol example)

Installation Instructions and Getting Started
=============================================
1. Use "pip" to install the "niflexlogger-automation" package, and any additonal packages::

	$ python -m pip install niflexlogger-automation

2. If running a Test Sequencer example, open the configuration file (config.csv) next to the example and modify the first column to point to a FlexLogger project. By default, the example will point to the included FlexLogger project. 

3. Run the example by using the following command through the command line interface::

	$ python "<ExamplePath>\ExampleName.py" "<Additional parameters, if needed>"

Related Resources
=================
For additional information about using the FlexLogger Python API and FlexLogger examples, refer the Read the Docs website at 'this link <https://niflexlogger-automation.readthedocs.io/en/latest>"_.

Copyright
(c) 2021 National Instruments Corporation. All rights reserved.