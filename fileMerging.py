# fileMerging.py | Merges two 3D images of same brain acquired from
# opposite directions, based on threshold values obtained from the
# "edge detection" step.
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
merged_dir = parameters[2]
reg_dir = parameters[3]


brains = parameters[4].split(",")

sag_size = ast.literal_eval(parameters[5])
cor_size = ast.literal_eval(parameters[6])

hor_size = []
temp = parameters[7].split(",")
for i in range(0,len(temp)):
    hor_size.append(ast.literal_eval(temp[i]))

n_stain = []
temp = parameters[8].split(",")
for i in range(0,len(temp)):
    n_stain.append(ast.literal_eval(temp[i]))

m_stain = []
temp = parameters[9].split(",")
for i in range(0,len(temp)):
    m_stain.append(ast.literal_eval(temp[i]))

n_fluo = []
temp = parameters[10].split(",")
for i in range(0,len(temp)):
    n_fluo.append(ast.literal_eval(temp[i]))

m_fluo = []
temp = parameters[11].split(",")
for i in range(0,len(temp)):
    m_fluo.append(ast.literal_eval(temp[i]))

log = parameters[12]



# Checking the parameters

print "The method will: "
print " - read NIfTI-1 from "+nii_dir
print " - read ASCII from "+ascii_dir
print " - save registration data to "+reg_dir
print " - save merged NIfTI-1 to "+merged_dir
print " - save the log data to "+log

print "\nBrains to be processed: "
print brains



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
    output_message = strftime("%H:%M:%S", localtime())+": Starting to process brain "+brains[i]
    print output_message
    log_file.write(output_message+"\n")
    
    DV_stain = nii_dir+"DV_"+brains[i]+"_nuclear_aligned_VD.nii.gz"
    VD_stain = nii_dir+"VD_"+brains[i]+"_nuclear.nii.gz"
    DV_fluo = nii_dir+"DV_"+brains[i]+"_geneExp_aligned_VD.nii.gz"
    VD_fluo = nii_dir+"VD_"+brains[i]+"_geneExp.nii.gz"

    ascii_DV_stain = ascii_dir+"DV_"+brains[i]+"_nuclear.txt"
    ascii_VD_stain = ascii_dir+"VD_"+brains[i]+"_nuclear.txt"
    ascii_DV_fluo = ascii_dir+"DV_"+brains[i]+"_geneExp.txt"
    ascii_VD_fluo = ascii_dir+"VD_"+brains[i]+"_geneExp.txt"
    
    ascii_merged_stain = ascii_dir+"merged_"+brains[i]+"_nuclear.txt"
    ascii_merged_fluo = ascii_dir+"merged_"+brains[i]+"_geneExp.txt"
    
    merged_stain = merged_dir+brains[i]+"_nuclear.nii.gz"
    merged_fluo = merged_dir+brains[i]+"_geneExp.nii.gz"

    temp_stain_1 = merged_dir+"temp_nuclear_1.nii.gz"
    temp_fluo_1 = merged_dir+"temp_geneExp_1.nii.gz"
    temp_stain_2 = merged_dir+"temp_nuclear_2.nii.gz"
    temp_fluo_2 = merged_dir+"temp_geneExp_2.nii.gz"
    
    
    # Edge-based C-implemented file merging
    
    output_message = strftime("%H:%M:%S", localtime())+": Merging ASCII files"
    print output_message
    log_file.write(output_message+"\n")

    cmd = "./file_merging "+str(hor_size[i])+" "+str(sag_size)+" "+str(cor_size)+" "+ascii_DV_stain+" "+ascii_VD_stain+" "+ascii_merged_stain+" "+str(n_stain[i])+" "+str(m_stain[i])
    call([cmd],shell=True)
    
    cmd = "./file_merging "+str(hor_size[i])+" "+str(sag_size)+" "+str(cor_size)+" "+ascii_DV_fluo+" "+ascii_VD_fluo+" "+ascii_merged_fluo+" "+str(n_fluo[i])+" "+str(m_fluo[i])
    call([cmd],shell=True)
    
    
    # Converting from ASCII to NIfTI-1

    output_message = strftime("%H:%M:%S", localtime())+": Converting merged file to NIfTI-1"
    print output_message
    log_file.write(output_message+"\n")

    cmd = "fslascii2img "+ascii_merged_stain+" "+str(sag_size)+" "+str(cor_size)+" "+str(hor_size[i])+" 1 0.0258 0.0258 0.04 1 "+temp_stain_1
    call([cmd],shell=True)
    
    cmd = "fslascii2img "+ascii_merged_fluo+" "+str(sag_size)+" "+str(cor_size)+" "+str(hor_size[i])+" 1 0.0258 0.0258 0.04 1 "+temp_fluo_1
    call([cmd],shell=True)
    
    
    # Re-orienting the merged NIfTI-1 file
   
    output_message = strftime("%H:%M:%S", localtime())+": Reorienting"
    print output_message
    log_file.write(output_message+"\n")

    cmd = "c3d "+temp_stain_1+" -orient RAI -o "+temp_stain_2+" && rm "+temp_stain_1
    call([cmd],shell=True)
    
    cmd = "c3d "+temp_fluo_1+" -orient RAI -o "+temp_fluo_2+" && rm "+temp_fluo_1
    call([cmd],shell=True)
    

    # Registration to original VD_stain
    
    output_message = strftime("%H:%M:%S", localtime())+": Registration"
    print output_message
    log_file.write(output_message+"\n")

    reg = reg_dir+"merged_reg_"+brains[i]+"_.nii"
    log = reg_dir+"log_merged_"+brains[i]+".txt"

    cmd = "ANTS 3 -i 0 -o "+reg+" --MI-option 64x300000 -m CC["+VD_stain+","+temp_stain_2+",1,5] >> "+log
    call([cmd],shell=True)
    

    # Alignment

    output_message = strftime("%H:%M:%S", localtime())+": Alignment"
    print output_message
    log_file.write(output_message+"\n")
    
    cmd = "WarpImageMultiTransform 3 "+temp_stain_2+" "+merged_stain+" -R "+VD_stain+" "+reg[:-4]+"Affine.txt"
    call([cmd],shell=True)
    cmd = "WarpImageMultiTransform 3 "+temp_fluo_2+" "+merged_fluo+" -R "+VD_stain+" "+reg[:-4]+"Affine.txt"
    call([cmd],shell=True)
    cmd = "rm "+temp_stain_2+" "+temp_fluo_2
    call([cmd],shell=True)


output_message = strftime("%H:%M:%S", localtime())+": Done."
print output_message
log_file.write(output_message+"\n")

log_file.close()
