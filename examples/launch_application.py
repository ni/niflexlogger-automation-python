# TODO - for now, have to do this at the command prompt:
# set PYTHONPATH=c:\dev\bparrott-flexlogger-automation-python
from flexlogger import Application

with Application() as a:
    a.open_project(path=r'C:\Users\gstoll\Documents\FlexLogger Projects\downsampling demo\downsampling demo.flxproj')