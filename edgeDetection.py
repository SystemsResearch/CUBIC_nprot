# edgeDetection.py | Measures the "edge content" of horizontal slices of
# two 3D images of same brain acquired from opposite directions.
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

nii_dir = parameters[0]
ascii_dir = parameters[1]

brains = parameters[2].split(",")

sag_size = ast.literal_eval(parameters[3])
cor_size = ast.literal_eval(parameters[4])

hor_size = []
temp = parameters[5].split(",")
for i in range(0,len(temp)):
    hor_size.append(ast.literal_eval(temp[i]))

log = parameters[6]
results_file = parameters[7]



# Checking the parameters

print "The method will: "
print " - read from "+nii_dir
print " - save ASCII files to "+ascii_dir
print " - save the log data to "+log

print "\nBrains to be processed: "
print brains

print "\nBrain size: "
print "- sagittal: "+str(sag_size)
print "- coronal: "+str(cor_size)
print "- horizontal: "+str(hor_size)


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




for i in range(0,len(brains)):
    br = brains[i]
    output_message = strftime("%H:%M:%S", localtime())+": Starting to process brain "+br
    print output_message
    log_file.write(output_message+"\n")

    DV_stain = nii_dir+"DV_"+br+"_nuclear_aligned_VD.nii.gz"
    VD_stain = nii_dir+"VD_"+br+"_nuclear.nii.gz"
    DV_fluo = nii_dir+"DV_"+br+"_geneExp_aligned_VD.nii.gz"
    VD_fluo = nii_dir+"VD_"+br+"_geneExp.nii.gz"

    ascii_DV_stain = ascii_dir+"DV_"+br+"_nuclear.txt"
    ascii_VD_stain = ascii_dir+"VD_"+br+"_nuclear.txt"
    ascii_DV_fluo = ascii_dir+"DV_"+br+"_geneExp.txt"
    ascii_VD_fluo = ascii_dir+"VD_"+br+"_geneExp.txt"


    # Converting from NIfTI-1 to ASCII
    
    output_message = strftime("%H:%M:%S", localtime())+": Converting to ASCII"
    print output_message
    log_file.write(output_message+"\n")

    cmd = "fsl2ascii "+DV_stain+" "+ascii_DV_stain
    call([cmd],shell=True)
    cmd = "mv "+ascii_DV_stain+"00000 "+ascii_DV_stain
    call([cmd],shell=True)

    cmd = "fsl2ascii "+VD_stain+" "+ascii_VD_stain
    call([cmd],shell=True)
    cmd = "mv "+ascii_VD_stain+"00000 "+ascii_VD_stain
    call([cmd],shell=True)

    cmd = "fsl2ascii "+DV_fluo+" "+ascii_DV_fluo
    call([cmd],shell=True)
    cmd = "mv "+ascii_DV_fluo+"00000 "+ascii_DV_fluo
    call([cmd],shell=True)

    cmd = "fsl2ascii "+VD_fluo+" "+ascii_VD_fluo
    call([cmd],shell=True)
    cmd = "mv "+ascii_VD_fluo+"00000 "+ascii_VD_fluo
    call([cmd],shell=True)


    # Prewitt-based C-implemented edge detection

    output_message = strftime("%H:%M:%S", localtime())+": Edge detection - nuclear"
    print output_message
    log_file.write(output_message+"\n")

    cmd = "./edge_detection_Prewitt "+str(hor_size[i])+" "+str(sag_size)+" "+str(cor_size)+" "+ascii_DV_stain+" "+ascii_VD_stain+" >> "+results_file
    call([cmd],shell=True)


    # Prewitt-based C-implemented edge detection

    output_message = strftime("%H:%M:%S", localtime())+": Edge detection - geneExp"
    print output_message
    log_file.write(output_message+"\n")

    cmd = "./edge_detection_Prewitt "+str(hor_size[i])+" "+str(sag_size)+" "+str(cor_size)+" "+ascii_DV_fluo+" "+ascii_VD_fluo+" >> "+results_file
    call([cmd],shell=True)



output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")

log_file.close()
