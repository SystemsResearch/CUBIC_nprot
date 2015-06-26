# sameBrainAlignment.py | Aligns two 3D images of the same brain acquired
# from opposite directions.
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

nii_dir = parameters[0]
reg_dir = parameters[1]

brains = parameters[2].split(",")

reg_method = parameters[3]

log = parameters[4]



# Checking the parameters

print "The method will: "
print " - read from, and save to "+nii_dir
print " - save registration data to "+reg_dir
print " - save the log data to "+log

print "\nBrains to be processed: "
print brains

print "\nRegistration method: "
print reg_method

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

reg_param = ""
if reg_method == "affine":
    reg_param = "-i 0"
elif reg_method == "SyN":
    reg_param = "-i 10x10x10"
else:
    print "Unrecognised registration method."
    quit()


log_file = open(log,'w')


for br in brains:

    DV_stain = nii_dir+"DV_"+br+"_nuclear.nii.gz"
    DV_fluo = nii_dir+"DV_"+br+"_geneExp.nii.gz"
    VD_stain = nii_dir+"VD_"+br+"_nuclear.nii.gz"
    
    DV_stain_aligned = nii_dir+"DV_"+br+"_nuclear_aligned_VD.nii.gz"
    DV_fluo_aligned = nii_dir+"DV_"+br+"_geneExp_aligned_VD.nii.gz"
    
    reg = reg_dir+"internal_reg_"+br+"_.nii"
    log = reg_dir+"log_"+br+".txt"
    
    output_message = strftime("%H:%M:%S", localtime())+": Registering "+br
    print output_message
    log_file.write(output_message+"\n")

    cmd = "ANTS 3 "+reg_param+" -o "+reg+" --MI-option 64x30000 -m CC["+VD_stain+","+DV_stain+",1,5] >> "+log
    call([cmd],shell=True)

    output_message = strftime("%H:%M:%S", localtime())+": Aligning both nuclear staining and fluorescent signal files."
    print output_message
    log_file.write(output_message+"\n")
    
    if reg_method == "affine":
        cmd = "WarpImageMultiTransform 3 "+DV_stain+" "+DV_stain_aligned+" -R "+VD_stain+" "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
        cmd = "WarpImageMultiTransform 3 "+DV_fluo+" "+DV_fluo_aligned+" -R "+VD_stain+" "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
    
    if reg_method == "SyN":
        cmd = "WarpImageMultiTransform 3 "+DV_stain+" "+DV_stain_aligned+" -R "+VD_stain+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
        cmd = "WarpImageMultiTransform 3 "+DV_fluo+" "+DV_fluo_aligned+" -R "+VD_stain+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)


output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")

log_file.close()
