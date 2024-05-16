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

def run_model(projectFileName, plan_name, PlanCount):
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
    
    # Set plan for next run
    _RASController.Plan_SetCurrent(plan_name)
    _RASController.PlanOutput_SetCurrent(plan_name)
    
    # start running the model
    _RASController.Compute_ShowComputationWindow()
    
    # initial the two variables for run step
    status = None
    messages = None
    
    # The real running command 
    res = _RASController.Compute_CurrentPlan(status, messages)
    
    # print computing message
    bRunSucessful = True
    
    if res[0]:
        print("HEC-RAS computed successfully.")
    else:
        print("HEC-RAS computed unsuccessfully.")
        bRunSucessful = False
        
    print("The returned messages are:")
    print("res = ", res)
    
    # Close project
    _RASController.Project_Close()
    
    # Quit RAS
    _RASController.QuitRas()
    
    terminate_hec_ras_process()