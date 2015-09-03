import os

STRESS = ['none','full','collapsed']

for stress in STRESS[:1]:
    os.system('qsub -cwd -l longq=1 -N %s-stress ./barley.submit.sh --stress %s' % (stress, stress))
