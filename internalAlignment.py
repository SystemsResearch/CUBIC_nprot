# internalAlignment.py | Aligns individual brain samples to an internal
# reference brain chosen by the user.
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
internal_ref = parameters[3]

reg_method = parameters[4]

log = parameters[5]



# Checking the parameters

print "The method will: "
print " - read NIfTI-1 from "+nii_dir
print " - save registration data to "+reg_dir

print "\nBrains to be processed: "
print brains

print "\nInternal reference brain: "
print internal_ref

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


ref_stain = nii_dir+internal_ref+"_nuclear.nii.gz"

for i in range(0,len(brains)):
    output_message = strftime("%H:%M:%S", localtime())+": Starting to process brain "+brains[i]
    print output_message
    log_file.write(output_message+"\n")


    if internal_ref == brains[i]:
        output_message = "\t\t(internal reference brain, skipped)"
        print output_message
        log_file.write(output_message+"\n")
        continue

    current_stain = nii_dir+brains[i]+"_nuclear.nii.gz"
    current_fluo = nii_dir+brains[i]+"_geneExp.nii.gz"
    aligned_stain = nii_dir+brains[i]+"_nuclear_aligned_"+internal_ref+".nii.gz"
    aligned_fluo = nii_dir+brains[i]+"_geneExp_aligned_"+internal_ref+".nii.gz"

    # Registration

    output_message = strftime("%H:%M:%S", localtime())+": Registration"
    print output_message
    log_file.write(output_message+"\n")

    reg = reg_dir+"merged_reg_"+brains[i]+"_to_"+internal_ref+"_.nii"
    log = reg_dir+"log_"+brains[i]+"_to_"+internal_ref+"_.txt"

    cmd = "ANTS 3 "+reg_param+" -o "+reg+" --MI-option 64x300000 -m CC["+ref_stain+","+current_stain+",1,5] >> "+log
    
    call([cmd],shell=True)


    # Alignement

    output_message = strftime("%H:%M:%S", localtime())+": Alignment"
    print output_message
    log_file.write(output_message+"\n")

    if reg_method == "affine":
        cmd = "WarpImageMultiTransform 3 "+current_stain+" "+aligned_stain+" -R "+ref_stain+" "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
        cmd = "WarpImageMultiTransform 3 "+current_fluo+" "+aligned_fluo+" -R "+ref_stain+" "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)

    if reg_method == "SyN":
        cmd = "WarpImageMultiTransform 3 "+current_stain+" "+aligned_stain+" -R "+ref_stain+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
        cmd = "WarpImageMultiTransform 3 "+current_fluo+" "+aligned_fluo+" -R "+ref_stain+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)


output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")
