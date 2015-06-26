# median_brainOnly | Calculates the median signal intensity for a series
# of brain samples, only considering the signal inside the brain.
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


import glob
from time import localtime, strftime
from subprocess import call
import ast
import numpy
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
ana_dir = parameters[2]

brains = parameters[3].split(",")
internal_ref = parameters[4]
atlas = parameters[5]

reg_method = parameters[6]

log = parameters[7]


# Checking the parameters

print "The method will: "
print " - read NIfTI-1 from "+nii_dir
print " - load registration data to "+reg_dir
print " - save ASCII data to "+ana_dir

print "\nBrains to be processed: "
print brains

print "\nInternal reference brain: "
print internal_ref

print "\nRegistration method used in steps 4-5: "
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


log_file = open(log,'w')

internal_reference = nii_dir+internal_ref+"_nuclear.nii.gz"

warp = reg_dir+"merged_reg_"+internal_ref+"_to_Atlas_InverseWarp.nii"
affine = reg_dir+"merged_reg_"+internal_ref+"_to_Atlas_Affine.txt"

aligned_atlas =nii_dir+"atlas_aligned_to_"+internal_ref+".nii.gz"
ascii_atlas = ana_dir+"atlas.txt"




# (assumes the list is already sorted)
def median(l):
    half = len(l) / 2
    if len(l) % 2 == 0:
        return (l[half-1] + l[half]) / 2.0
    else:
        return l[half]





# Alignment of the atlas to the internal reference
# Note:
#   - the internal reference has already been registered to the atlas
#   - because we use the reverse transformation, the order is affine-warp, instead of warp-affine, if using SyN

if reg_method != "affine" and reg_method != "SyN":
    print "Unrecognised registration method."
    quit()

output_message = strftime("%H:%M:%S", localtime())+": Atlas alignment.\n"
print output_message
log_file.write(output_message+"\n")

if reg_method == "affine":
    cmd = "WarpImageMultiTransform 3 "+atlas+" "+aligned_atlas+" -R "+internal_reference+" -i "+affine
    call([cmd],shell=True)

if reg_method == "SyN":
    cmd = "WarpImageMultiTransform 3 "+atlas+" "+aligned_atlas+" -R "+internal_reference+" -i "+affine+" "+warp
    call([cmd],shell=True)


# Exporting aligned brain atlas to ASCII

output_message = strftime("%H:%M:%S", localtime())+": Atlas export.\n"
print output_message
log_file.write(output_message+"\n")

cmd = "fsl2ascii "+aligned_atlas+" "+ascii_atlas
call([cmd],shell=True)
cmd = "mv "+ascii_atlas+"00000 "+ascii_atlas
call([cmd],shell=True)

output_message = strftime("%H:%M:%S", localtime())+": Atlas loading."
print output_message
log_file.write(output_message+"\n")

atlas_data = []
inFile = open(ascii_atlas,'r')
for line in inFile:
    tempArray = line.rstrip().split(" ")
    if len(tempArray)>1:
        for val in tempArray:
            atlas_data.append(ast.literal_eval(val))
inFile.close()
output_message = "\t\t"+str(len(atlas_data))+" pixels"
print output_message
log_file.write(output_message+"\n")


# Processing each brain
for i in range(0,len(brains)):

    output_message = "\n"+strftime("%H:%M:%S", localtime())+": Brain "+brains[i]
    print output_message
    log_file.write(output_message+"\n")

    filename = nii_dir+brains[i]+"_geneExp_aligned_"+internal_ref+".nii.gz"
    if brains[i]==internal_ref:
        filename = nii_dir+brains[i]+"_geneExp.nii.gz"
    ascii_brain = ana_dir+brains[i]+".txt"
    
    # Exporting to ASCII

    output_message = strftime("%H:%M:%S", localtime())+":\tExporting."
    print output_message
    log_file.write(output_message+"\n")

    cmd = "fsl2ascii "+filename+" "+ascii_brain
    call([cmd],shell=True)
    cmd = "mv "+ascii_brain+"00000 "+ascii_brain
    call([cmd],shell=True)


    # Loading

    output_message = strftime("%H:%M:%S", localtime())+":\tLoading."
    print output_message
    log_file.write(output_message+"\n")

    brain_data = []
    inFile = open(ascii_brain,'r')
    for line in inFile:
        tempArray = line.rstrip().split(" ")
        if len(tempArray)>1:
            for val in tempArray:
                brain_data.append(ast.literal_eval(val))
    inFile.close()
    output_message = "\t\t"+str(len(brain_data))+" pixels"
    print output_message
    log_file.write(output_message+"\n")


    # Filtering
    output_message = strftime("%H:%M:%S", localtime())+":\tFiltering."
    print output_message
    log_file.write(output_message+"\n")

    filtered_brain_data = []
    for i in range(0,len(brain_data)):
        if atlas_data[i]>=1:
            filtered_brain_data.append(brain_data[i])
    output_message = "\t\t"+str(len(filtered_brain_data))+" pixels"
    print output_message
    log_file.write(output_message+"\n")


    # Median
    output_message = strftime("%H:%M:%S", localtime())+":\tMedian: "
    print output_message
    log_file.write(output_message+"\n")

    filtered_brain_data.sort()
    med = median(filtered_brain_data)
    output_message = "\t\t"+str(med)
    print output_message
    log_file.write(output_message+"\n")



output_message = "\n"+strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")


log_file.close()
