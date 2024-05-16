import sys
import numpy as np
import h5py
import pyvista as pv
import os.path
import copy

from Zeda_Auto_2D_RAS import get_ras_version

class Data_Postprocess():
    
    # Initial the class
    def __init__(self, hdf_filename, dir_path):
        
        # saving inputs to self.variables
        self.hdf_filename = hdf_filename
        self.dir_path = dir_path
        
        self.plan_filename = self.hdf_filename[:-4]
        self.plan = self.plan_filename[:-3]
        self.project_filename = self.plan_filename[:-4] + '.prj'
        
        self.comp_indicator = "Computation Interval="
        self.comp_interval = ''
        
        self.outp_indicator = "Output Interval="
        self.output_interval = ''
        
        self.map_indicator = "Mapping Interval="
        self.map_interval = ''
        
        self.time_indicator = "Simulation Date="
        self.start_time = ''
        self.end_time = ''
        self.Dpart = ''
    
    ###################################################################################
    #  Get some fundamental info, e.g. start and end time, unit, output interval      #
    ###################################################################################
    
    # Get which verison of HEC-RAS is the hdf file runned by
    def get_runned_RAS_version_from_version(self, hdf_filename, dir_path):
        hf = h5py.File(dir_path + hdf_filename, 'r')
        file_version = hf.attrs['File Version']
        return file_version
        
    def check_same_version(self, runned_ras_version, installed_ras_version):
        
        runned_ras_version = get_runned_RAS_version_from_version(self.hdf_filename, self.dir_path)
        installed_ras_version = get_ras_version()
        
        same_version = ''
        if runned_ras_version == installed_ras_version:
            print('Same Version.')
            same_version = True
        else:
            print('Different Version')
            same_version = False
        return same_version
    
    def get_units(self, project_filename, dir_path):
        with open(dir_path + project_filename,'r') as project_file:
            lines = project_file.readlines()
            if "English Units" in lines[3]:
                return 'Feet'
            elif "SI Units" in lines[3]:
                return 'Meter'
            else:
                return "Unknown units"
    
    def get_computation_interval(self, dir_path):
        with open(dir_path + self.plan + 'p01','r') as plan_file:
            for line in plan_file:
                if comp_indicator in line:
                    comp_interval = line[line.index(comp_indicator) + len(comp_indicator):].rpartition("\n")[0]
        
        self.comp_interval = comp_interval
        return self.comp_interval
    
    def get_output_interval(self, dir_path):
        with open(dir_path + self.plan + 'p01','r') as plan_file:
            for line in plan_file:
                if outp_indicator in line:
                    outp_interval = line[line.index(outp_indicator) + len(outp_indicator):].rpartition("\n")[0]
                    break
        
        self.output_interval = outp_interval
        return self.output_interval
    
    def get_map_interval(self, dir_path):
        with open(dir_path + plan + 'p01','r') as plan_file:
            for line in plan_file:
                if map_indicator in line:
                    map_interval = line[line.index(map_indicator) + len(map_indicator):].rpartition("\n")[0]
                    break
        self.map_interval = map_interval
        return self.map_interval
        
    def get_start_and_end_time(self, dir_path):
        with open(dir_path + plan + 'p01','r') as plan_file:
            for line in plan_file:
                if time_indicator in line:
                    time_line = line
                    break
        
        times = time_line[time_line.index(time_indicator) + len(time_indicator):]
        
        start_time = times[0:15]
        start_time = start_time.replace(","," ")
        
        end_time = times[16:-1]
        end_time = end_time.replace(","," ")
        
        Dpart = start_time[0:9]
        
        self.start_time = start_time
        self.end_time = end_time
        self.Dpart = Dpart
        return  self.start_time, self.end_time, self.Dpart
    
    ##################################################################################
    #  Get some real important stuff, e.g. x, y, z, elevation, WSE, Water depth      #
    ##################################################################################
    
    # Function use to extra x, y coordinates, and elevation
    def get_3D_data(self, hdf_filename, dir_path):
        hf = h5py.File(dir_path + hdf_filename, 'r')
        
        hdf2DAreaCellPoints = np.array(hf['Geometry']['2D Flow Areas']['Cell Points'])
        hdf2DAreaCellElevation = np.array(hf['Geometry']['2D Flow Areas']['Perimeter 1']['Cells Minimum Elevation'])
        hdf2DAreaCellElevationCor = np.array(hf['Geometry']['2D Flow Areas']['Perimeter 1']['Cells Center Coordinate'])
        
        hf.close()
        
        hdf2DAreaCellCoordinates3D = np.zeros((hdf2DAreaCellPoints.shape[0], 3))
        
        for i in range (hdf2DAreaCellPoints.shape[0]):
            hdf2DAreaCellCoordinates3D[i, 0] = hdf2DAreaCellPoints[i, 0]
            hdf2DAreaCellCoordinates3D[i, 1] = hdf2DAreaCellPoints[i, 1]
            hdf2DAreaCellCoordinates3D[i, 2] = hdf2DAreaCellElevation[i]
            
        return hdf2DAreaCellCoordinates3D
        
    # Extract calculated WSE from HDF5
    def get_WSE(self, hdf_filename, dir_path):
        hf = h5py.File(dir_path + hdf_filename, 'r')
        
        hdf2DAreaCellWSE = np.array(hf['Results']['Unsteady']['Output']['Output Blocks']['Base Output']['Unsteady Time Series']['2D Flow Areas']['Perimeter 1']['Water Surface'])
        
        hf.close()
        
        return hdf2DAreaCellWSE
    
    # Extract maximum WSE from HDF5
    def get_max_WSE(self, hdf_filename, dir_path):
        hf = h5py.File(dir_path + hdf_filename, 'r')
        
        hdf2DAreaCellWSE = np.array(hf['Results']['Unsteady']['Output']['Output Blocks']['Base Output']['Unsteady Time Series']['2D Flow Areas']['Perimeter 1']['Water Surface'])
        
        hf.close()
        
        hdf2DAreaCellMaxWSE = np.zeros(hdf2DAreaCellWSE.shape[1])
        
        for i in range (hdf2DAreaCellWSE.shape[1]):
            hdf2DAreaCellMaxWSE[i] = hdf2DAreaCellWSE[:, i].max()
        
        return hdf2DAreaCellMaxWSE
        
    # The total dataset on cell, 6 columes, x, y, 0 (z vaule for further VTK), elevation, WSE, Water Depth
    def get_entire_numpy_dataset(self, hdf2DAreaCellCoordinates3D, hdf2DAreaCellMaxWSE):
        hdf2DAreaCell6D = np.zeros((hdf2DAreaCellCoordinates3D.shape[0], 6))
        
        for i in range (hdf2DAreaCellCoordinates3D.shape[0]):
            hdf2DAreaCell6D[i, 0] = hdf2DAreaCellCoordinates3D[i, 0]
            hdf2DAreaCell6D[i, 1] = hdf2DAreaCellCoordinates3D[i, 1]
            hdf2DAreaCell6D[i, 2] = 0
            hdf2DAreaCell6D[i, 3] = hdf2DAreaCellCoordinates3D[i, 2]
            hdf2DAreaCell6D[i, 4] = hdf2DAreaCellMaxWSE[i]
            hdf2DAreaCell6D[i, 5] = hdf2DAreaCell6D[i, 4] - hdf2DAreaCell6D[i, 3]
            
        return hdf2DAreaCell6D
    
    # convert numpy data to vtk format (in surface format)
    def np_to_surface_vtk(self, hdf2DAreaCell6D):
        coords = hdf2DAreaCell6D
        
        # Create a point cloud with the coordinate values
        point_cloud = pv.PolyData(coords[:, :3])
        
        # Add scalar values to the point cloud
        point_cloud.point_data['elevation'] = coords[:, 3]
        point_cloud.point_data['WSE'] = coords[:, 4]
        point_cloud.point_data['Water Depth'] = coords[:, 5]
        
        surf = point_cloud.delaunay_2d()
        
        # Save the interpolated surface as a VTK file
        surf.save('output_surface.vtk')
        
    def np_to_points_vtk(self, hdf2DAreaCell6D):
        coords = hdf2DAreaCell6D
        
        # Create a point cloud with the coordinate values
        point_cloud = pv.PolyData(coords[:, :3])
        
        # Add scalar values to the point cloud
        point_cloud.point_data['elevation'] = coords[:, 3]
        point_cloud.point_data['WSE'] = coords[:, 4]
        point_cloud.point_data['Water Depth'] = coords[:, 5]
        
        # Save the point cloud as a VTK file
        point_cloud.save('output_ponits.vtk')