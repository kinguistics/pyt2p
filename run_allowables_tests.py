import os


os.system('qsub -cwd -l longq=1 -N test-allowables ./barley.submit.sh')
