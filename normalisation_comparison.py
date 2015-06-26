# normalisation_comparison | "Normalises" a number of 3D brain images
# by applying factors based on the median signal intensity calculated at
# the previous step.
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

merged_dir = parameters[0]

brains = parameters[1].split(",")
internal_ref = parameters[2]

temp = parameters[3].split(",")
median = dict()
for i in range(0,len(brains)):
    median[brains[i]] = ast.literal_eval(temp[i])

neg_brain = parameters[4]
pos_brain = parameters[5]

log = parameters[6]


# Checking the parameters

print "The method will: "
print " - read/write NIfTI-1 from/to "+merged_dir

print "\nBrains to be processed: "
print brains

print "\nInternal reference brain: "
print internal_ref

print "\nMedian intensity: "
print median

print "\nNegative (control) brain: "
print neg_brain

print "\nPositive brain: "
print pos_brain


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



# calculating the highest value
highestMedian = 0
for el in median:
    val = median[el]
    if val > highestMedian:
        highestMedian = val


# Normalisation

output_message = strftime("%H:%M:%S", localtime())+": Normalising."
print output_message
log_file.write(output_message+"\n")


for i in range(0,len(brains)):

    normalisationFactor = highestMedian/median[brains[i]]

    raw = merged_dir+brains[i]+"_geneExp_aligned_"+internal_ref+".nii.gz"
    normd = merged_dir+brains[i]+"_geneExp_aligned_"+internal_ref+"_normalised.nii.gz"
    if brains[i]==internal_ref:
        raw = merged_dir+brains[i]+"_geneExp.nii.gz"
        normd = merged_dir+brains[i]+"_geneExp_normalised.nii.gz"

    cmd = "fslmaths "+raw+" -mul "+str(normalisationFactor)+" "+normd
    call([cmd],shell=True)



# Difference between two brains

output_message = strftime("%H:%M:%S", localtime())+": Subtracting brains."
print output_message
log_file.write(output_message+"\n")

neg = merged_dir+neg_brain+"_geneExp_aligned_"+internal_ref+"_normalised.nii.gz"
if neg_brain == internal_ref:
    neg = merged_dir+neg_brain+"_geneExp_normalised.nii.gz"

pos = merged_dir+pos_brain+"_geneExp_aligned_"+internal_ref+"_normalised.nii.gz"
if pos_brain == internal_ref:
    pos = merged_dir+pos_brain+"_geneExp_normalised.nii.gz"

diff = merged_dir+"sub_"+neg_brain+"_from_"+pos_brain+"_normalised.nii.gz"
cmd = "fslmaths "+pos+" -sub "+neg+" "+diff
call([cmd],shell=True)


output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")

log_file.close()
