# convertTiffFiles.py | Converts stacks of TIFF images to NIfTI-1 3D images.
# Please see the user manual for details.
#
# Copyright (C) 2015, Dimitri Perrin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import glob
from time import localtime, strftime
from subprocess import call
import ast
import sys


if len(sys.argv)!=2:
    print "\nUsage: "+sys.argv[0]+" <parameter_file>"
    quit()



# Reading the parameters

parameter_file = open(sys.argv[1],'r')
parameters = []
for line in parameter_file:
    if line[0] == "#":
        continue
    parameters.append(line.rstrip())
parameter_file.close()



# Processing the parameters

initial_dir = parameters[0]
nii_dir = parameters[1]
temp_dir = parameters[2]


XY_resolution = ast.literal_eval(parameters[3])
Z_step = ast.literal_eval(parameters[4])
factor = ast.literal_eval(parameters[5])
step = ast.literal_eval(parameters[6])

scaling=str(factor*100)+"%"

direction_start = ast.literal_eval(parameters[7].split(",")[0])
direction_end = ast.literal_eval(parameters[7].split(",")[1])

brainID_start = ast.literal_eval(parameters[8].split(",")[0])
brainID_end = ast.literal_eval(parameters[8].split(",")[1])

signal_start = ast.literal_eval(parameters[9].split(",")[0])
signal_end = ast.literal_eval(parameters[9].split(",")[1])

log = parameters[10]




# Checking the parameters

print "The method will: "
print " - read data from "+initial_dir
print " - save results to "+nii_dir
print " - use "+temp_dir+" for temporary files"
print " - save the log data to "+log

print "\nThe raw image resolution is "+str(XY_resolution)+"mm in the XY direction, and "+str(Z_step)+"mm in the Z direction."
print "The NIfTI files will be downscaled to "+scaling+" in the XY direction, and by a factor of "+str(step)+" in the Z direction."

list_samples = glob.glob(initial_dir+"*")
example = list_samples[0][len(initial_dir):]

print "\nA typical file format is: "+example
print "In that file: "
print "- the acquisition direction is "+example[direction_start:direction_end]
print "- the brain ID is "+example[brainID_start:brainID_end]
print "- the signal is "+example[signal_start:signal_end]

print " "
while 1:
    feedback = raw_input("Is this correct? (yes/no)\t").rstrip()
    if feedback == "yes":
        print "Program starting...\n"
        break
    if feedback == "no":
        print "Please edit the parameter file."
        quit()




# Running the analysis step

log_file = open(log,'w')

for s in list_samples:
    sample_dir = s[len(initial_dir):]
    direction = sample_dir[direction_start:direction_end]
    brainID = sample_dir[brainID_start:brainID_end]
    nbSlices = len(glob.glob(initial_dir+sample_dir+"/*"))
    signal = sample_dir[signal_start:signal_end]

    name = direction+"_"+brainID+"_"+signal
    output_message = strftime("%H:%M:%S", localtime())+": Starting to process "+name
    print output_message
    log_file.write(output_message+"\n")


    if len(glob.glob(nii_dir+name+".nii.gz"))>0:
        output_message = strftime("%H:%M:%S", localtime())+": \tNIfTI-1 file already available. Moving on to next file."
        print output_message
        log_file.write(output_message+"\n")
        continue

    output_message = strftime("%H:%M:%S", localtime())+": \tStarting to convert Tiff files."
    print output_message
    log_file.write(output_message+"\n")

    # Convert (and rescale) original Tiff files
    for i in range(0,nbSlices,step):
        slice = "%04d" % (i)
        outfile = "%03d" % (i/step)
        file = initial_dir+sample_dir+"/*Z"+slice+"*.ome.tif"
        
        call(["convert",file,"-resize",scaling,"-depth","16",temp_dir+outfile+".tif"])

    output_message = strftime("%H:%M:%S", localtime())+": \tDone."
    print output_message
    log_file.write(output_message+"\n")

    # Create 3D volume as NII file

    orient = " -orient RAI "
    if direction == "DV":
        orient = " -orient RAS "
    elif direction != "VD":
        output_message = "Error in direction detection?"
        print output_message
        log_file.write(output_message+"\n")

        quit()
    scale = " -spacing "+str(XY_resolution/factor)+"x"+str(XY_resolution/factor)+"x"+str(Z_step*step)+"mm "
    cmd = "c3d "+temp_dir+"*.tif -tile z "+orient+scale+" -o "+nii_dir+name+".nii.gz"

    output_message = strftime("%H:%M:%S", localtime())+": \tStarting construct the 3D volume."
    print output_message
    log_file.write(output_message+"\n")

    call([cmd],shell=True)
    output_message = strftime("%H:%M:%S", localtime())+": \tDone."
    print output_message
    log_file.write(output_message+"\n")

    # Remove the temporary files
    for tempFile in glob.glob(temp_dir+"*.tif"):
        os.remove(tempFile)


log_file.close()

quit()

