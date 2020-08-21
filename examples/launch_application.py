from flexlogger import Application

with Application() as a:
    project = a.open_project(path=r'C:\Users\gstoll\Documents\FlexLogger Projects\downsampling demo\downsampling demo.flxproj')
    print("Press any key to close project...")
    input()
    project.close(allow_prompts=False)