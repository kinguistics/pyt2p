#!/bin/bash

# Name the job in Grid Engine
#$ -N <job-name>

#tell grid engine to use current directory
#$ -cwd

# Set Email Address where notifications are to be sent
#$ -M etking@stanford.edu

# Tell Grid Engine to notify job owner if job 'b'egins, 'e'nds, 's'uspended is 'a'borted, or 'n'o mail
#$ -m besan

# Tel Grid Engine to join normal output and error output into one file 
#$ -j y


## the "meat" of the script

#just print the name of this machine
python train.py $*
