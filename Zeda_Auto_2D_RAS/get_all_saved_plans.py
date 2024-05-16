import os.path
import sys
import platform
import psutil

def terminate_hec_ras_process():
    for p in psutil.process_iter():
        try:
            if p.name().lower() == 'ras.exe':
                p.terminate()
        except psutil.Error:
            pass

def get_plan(projectFileName):
    # The inout plan name needs to be a string. (e.g. Plan 01) #
    
    if platform.system().startswith('Windows'):
        try:
            import win32com.client as win32
        except ImportError:
            raise ImportError('Error in importing pywin32 package. Make sure it has been installed properly.')
    
    # use win32 to enable controller, make sure use get_ras_version function first, to make sure there is using the correct version
    _RASController = win32.gencache.EnsureDispatch('RAS630.HECRASController')
    
    # projectFileName = 'C:/LeonDemo/Demo.prj'
    
    _project_file_name = os.path.abspath(projectFileName)
    
    # Open HEC-RAS
    _RASController.ShowRas()
    
    # Open Project
    _RASController.Project_Open(_project_file_name)
    
    # Show current project name
    title = _RASController.CurrentProjectTitle()
    
    #
    PlanCount = 0
    PlanNames = None
    
    IncludeOnlyPlansInBaseDirectory = False
    PlanCount, PlanNames, temp = _RASController.Plan_Names(None, None, IncludeOnlyPlansInBaseDirectory)
    
    print("There are ", PlanCount, "plan(s) in current project.")
    print('Plan names: ', PlanNames)  # returns plan names
    
    # Close project
    _RASController.Project_Close()
    
    # Quit RAS
    _RASController.QuitRas()
    
    terminate_hec_ras_process()
    
    return PlanCount, PlanNames