# exportTiffStack.py | Gives two examples of further operations:
# - one set of raw TIFF stacks is normalised using the same factors as in
#   the NIfTI-1 file normalisation
# - one set of NIfTI-1 files is exported to TIFF stacks
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
import glob
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

raw_dir = parameters[0]
nii_dir = parameters[1]
out_dir = parameters[2]

brains_norm = parameters[3].split(",")

temp = parameters[4].split(",")
median = dict()
for i in range(0,len(brains_norm)):
    median[brains_norm[i]] = ast.literal_eval(temp[i])

brains_conv = parameters[5].split(",")

nb_slices = ast.literal_eval(parameters[6])

log = parameters[7]


# Checking the parameters

print "The method will: "
print " - read raw files from "+raw_dir
print " - write normalised files to "+out_dir

print "\nBrains to be normalise: "
print brains_norm

print "\nMedian intensity: "
print median

print "\nBrains to be export: "
print brains_conv



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



####################################
####################################
##                                ##
## Normalising the raw (DV) TIFF  ##
##  stacks for the signal channel ##
##                                ##
####################################
####################################


# calculating the highest value
highestMedian = 0
for el in median:
    val = median[el]
    if val > highestMedian:
        highestMedian = val


for j in range(0,len(brains_norm)):

    normalisationFactor = highestMedian/median[brains_norm[j]]

    output_message = strftime("%H:%M:%S", localtime())+": Exporting results for brain "+brains_norm[j]
    print output_message
    log_file.write(output_message+"\n")

    name_stem = raw_dir+"*"+brains_norm[j]+"_geneExp_DV"
    dir_name = glob.glob(name_stem)[0]+"/"

    nb_images = len(glob.glob(dir_name+"*.tif"))
    for i in range(0,nb_images):
        img = dir_name+"*Z%04d*.ome.tif" % (i)
        cmd = "convert "+img+" -evaluate multiply "+str(normalisationFactor)+" "+out_dir+brains_norm[j]+"_geneExp_%04d.tif" % (i)
        call([cmd],shell=True)





##################################
##################################
##                              ##
## Exporting files from         ##
##  from NIfTI-1 to TIFF stack  ##
##                              ##
##################################
##################################

for b in brains_conv:
    output_message = strftime("%H:%M:%S", localtime())+": Exporting from NIfTI-1 to TIFF for brain "+b
    print output_message
    log_file.write(output_message+"\n")

    for sl in range(0,nb_slices):
        b_out = b+"_%03d.tif" % (sl)
        cmd = "c3d "+nii_dir+b+".nii.gz -slice z "+str(sl)+" -o "+out_dir+b_out
        call([cmd],shell=True)

output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")


log_file.close()
