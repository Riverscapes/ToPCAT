#!/usr/bin/env python

# This is a full workflow script to perform point cloud processing using pctools library
import os
from ctypes import *

# Depending on what is the current directory (directory of the python session) given by
#print os.getcwd()
# ... you may need to adjust paths below

# Let's load the dynamic library
# On Windows, it is pctools.dll
# The library has run-time dependencies:
#  some common dynamic run-time libraires hopefully present on your system

# Assuming the library is in the current directory
pctools = CDLL("pctools.dll")
# Otherwise, change to one similar to these
#pctools = CDLL("E:\\PointClouds\\x64\\pctools.dll")
#pctools = CDLL("../win64/pctools.dll")

# Some meta-data to help ctypes talk to the library
pctools.sortintoxygrid.argtypes = [c_wchar_p, c_double, c_double]
pctools.stats_detrended.argtypes = [c_wchar_p, c_double, c_double, c_double]

# Optionally set the number of threads for parallel sections inside pctools 
pctools.set_num_threads(2)


# One can also change the working directory
# output_directory = u"./"
# output_directory = u"../Data"
# os.chdir(output_directory)

# Cyclone can export point clouds in an ASCII .pts file
# This is currently the only import format allowed by pctools
# Assuming the pts file is in the current directory
pts = u"24_January_test_Rees.pts"

# Some GUI to help select the pts file
if not pts: 
	import wx
	app = wx.PySimpleApp()
	pts = wx.FileSelector()
	
# Extension-free filename
file_name = pts.rsplit('.',1)[0]

# This will be our main file holding the whole point cloud as a a binary linear memory-mapped array.
# Always give an extension
# Recommended extension .mmf which stands for memory-mapped file
pc_mmf = file_name + u".mmf"

# This will produce an unsorted pc_mmf, double precision
pctools.importpts(pts, pc_mmf)

# A textual description file is produced with some information about the pint cloud
# We can simply display it
# (do pay attention to xmax-xmin, ymax-ymin as it will determine your grid size;
# the outliers can stretch the range)
print
for line in open(file_name + u".ini", "r"):
	print line,
print
# or read it in the variables
#execfile(file_name + u".ini")






# Choose grid resolution and sort the points
xres = 0.1
yres = 0.1
# This will result in a sorted pc_mmf (under the same name)
# Shifts the center of coordinates to the Centroid of the whole dataset
# Stores the relative point xyz positions in float precision
# Produces cells indeces, datacells holding the pointers to the corresponding point groups
# Creates the stats file with cells centroids (other fields invalid)

pctools.sortintoxygrid(pc_mmf, xres, yres)


# Same description file is ammended with some parameters of the grid
#execfile(file_name + u".ini")

# Finalizes the stats file
pctools.stats(pc_mmf)

# Calculates the stats of "detrended" points
# Detrended against the "ground level"
# Ground level is piecewise-linear function or triangular mesh
# with the nodes at the centres of the cells elevated to
# cell_ground_level = times_zmin*zmin + times_zmean*zmean + times_stdev*stdev
times_zmin = 0
times_zmean = 1
times_stdev = 0

pctools.stats_detrended(pc_mmf, times_zmin, times_zmean, times_stdev)


# Export decimated point clouds, stats and detrended stats as ASCII files
# But only for cells populated at or above a threshold
min_npoints_per_cell_threshold = 4;
pctools.export_stats(pc_mmf, min_npoints_per_cell_threshold)

# Can stay in Python
#raw_input( '            ...completed. Press Enter to Quit' )
# Otherwise exit to the command-line
