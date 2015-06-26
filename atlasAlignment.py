# atlasAlignment.py | Aligns individual brain samples (already aligned to
# an internal reference) to a brain atlas.
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
atlas = parameters[4]

reg_method = parameters[5]

log = parameters[6]



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


# Registration of the internal reference to the atlas

output_message = strftime("%H:%M:%S", localtime())+": Registration of brain "+internal_ref
print output_message
log_file.write(output_message+"\n")

ref_stain = nii_dir+internal_ref+"_nuclear.nii.gz"
ref_fluo = nii_dir+internal_ref+"_geneExp.nii.gz"

aligned_stain = nii_dir+internal_ref+"_nuclear_aligned_Atlas.nii.gz"
aligned_fluo = nii_dir+internal_ref+"_geneExp_aligned_Atlas.nii.gz"

reg = reg_dir+"merged_reg_"+internal_ref+"_to_Atlas_.nii"
log = reg_dir+"log_"+internal_ref+"_to_Atlas.txt"

cmd = "ANTS 3 "+reg_param+" -o "+reg+" --MI-option 64x300000 -m CC["+atlas+","+ref_stain+",1,5] >> "+log
call([cmd],shell=True)


# Alignment of the internal reference to the atlas

output_message = strftime("%H:%M:%S", localtime())+": Alignment of brain "+internal_ref
print output_message
log_file.write(output_message+"\n")

if reg_method == "affine":
    cmd = "WarpImageMultiTransform 3 "+ref_stain+" "+aligned_stain+" -R "+atlas+" "+reg[:-4]+"Affine.txt"
    call([cmd],shell=True)
    cmd = "WarpImageMultiTransform 3 "+ref_fluo+" "+aligned_fluo+" -R "+atlas+" "+reg[:-4]+"Affine.txt"
    call([cmd],shell=True)

if reg_method == "SyN":
    cmd = "WarpImageMultiTransform 3 "+ref_stain+" "+aligned_stain+" -R "+atlas+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
    call([cmd],shell=True)
    cmd = "WarpImageMultiTransform 3 "+ref_fluo+" "+aligned_fluo+" -R "+atlas+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
    call([cmd],shell=True)


# Alignment of all other samples

for i in range(0,len(brains)):
    if internal_ref == brains[i]:
        continue
    
    output_message = strftime("%H:%M:%S", localtime())+": Alignment of brain "+brains[i]
    print output_message
    log_file.write(output_message+"\n")

    current_stain = nii_dir+brains[i]+"_nuclear_aligned_"+internal_ref+".nii.gz"
    current_fluo = nii_dir+brains[i]+"_geneExp_aligned_"+internal_ref+".nii.gz"

    aligned_stain = nii_dir+brains[i]+"_nuclear_aligned_"+internal_ref+"_aligned_Atlas.nii.gz"
    aligned_fluo = nii_dir+brains[i]+"_geneExp_aligned_"+internal_ref+"_aligned_Atlas.nii.gz"

    if reg_method == "affine":
        cmd = "WarpImageMultiTransform 3 "+current_stain+" "+aligned_stain+" -R "+atlas+" "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
        cmd = "WarpImageMultiTransform 3 "+current_fluo+" "+aligned_fluo+" -R "+atlas+" "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)

    if reg_method == "SyN":
        cmd = "WarpImageMultiTransform 3 "+current_stain+" "+aligned_stain+" -R "+atlas+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)
        cmd = "WarpImageMultiTransform 3 "+current_fluo+" "+aligned_fluo+" -R "+atlas+" "+reg[:-4]+"Warp.nii "+reg[:-4]+"Affine.txt"
        call([cmd],shell=True)


output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")

log_file.close()
