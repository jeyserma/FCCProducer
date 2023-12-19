
import sys
import os
import subprocess
import random
import config

######################################################
### CONFIG
######################################################
tag = "winter2023" # corresponds to detector configuration (and stack)
tag_gen = "winter2023" # where the cards are stored
pythia_card = "p8_ee_WW_ecm162p3_p50MeV" # Pythia card; different vertex distributions for z/h pole
name = f"{pythia_card}"

nevents = 10000
njobs = -1 # -1 means to run locally (dry run)

######################################################


cwd = os.getcwd()
stack = config.stacks[tag]
priority = 'group_u_FCC.local_gen'
queue = "longlunch" # espresso microcentury longlunch workday tomorrow testmatch nextweek


pythia_card_def = f"{cwd}/cards/{tag_gen}/generator/pythia/{pythia_card}.cmd"
delphes_card = f"{cwd}/cards/{tag_gen}/delphes/card_IDEA.tcl"
delphes_cfg_card = f"{cwd}/cards/{tag_gen}/delphes/edm4hep_IDEA.tcl"


submit_dir = f"{cwd}/submit/{tag}/{name}/"
out_dir = f"/eos/experiment/fcc/users/j/jaeyserm/sampleProduction/{tag}/{name}/"
local_dir = f"{cwd}/local/{tag}/{name}/"

def make(seed, savedir):
    
    fOutName = f"{savedir}/submit_{seed}.sh"
    if os.path.exists(fOutName):
        return -1
    rootOutName = f"events_{seed}.root"
    if os.path.exists(f"{out_dir}/{rootOutName}"):
        return -1
    
    fOut = open(fOutName, 'w')

    fOut.write('#!/bin/bash\n')
    fOut.write('SECONDS=0\n')
    fOut.write('unset LD_LIBRARY_PATH\n')
    fOut.write('unset PYTHONHOME\n')
    fOut.write('unset PYTHONPATH\n')
    fOut.write('mkdir job_%s\n'%seed)
    fOut.write('cd job_%s\n'%seed)
    fOut.write('source %s\n'%stack)

    # run PythiaDelphes and produce edm4hep
    fOut.write('echo "Run PythiaDelphes"\n')
    fOut.write('cp %s card.cmd\n'%pythia_card_def)
    fOut.write('cp %s card.tcl\n'%delphes_card)
    fOut.write('cp %s edm4hep_output_config.tcl\n'%delphes_cfg_card)

    fOut.write('echo "Random:seed = %s" >> card.cmd\n'%seed)
    fOut.write('echo "Main:numberOfEvents = %i" >> card.cmd\n'%(nevents))

    fOut.write('DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd %s\n'%rootOutName)
    fOut.write('echo "DONE"\n')
    
    fOut.write('echo "Copy file"\n')
    fOut.write('cp %s %s/\n'%(rootOutName,out_dir))
    
    fOut.write('duration=$SECONDS\n')
    fOut.write('echo "Duration: $(($duration))"\n')
    fOut.write('echo "Events: %d"\n'%nevents)

            
    subprocess.getstatusoutput('chmod 777 %s'%fOutName)
    return fOutName

if __name__=="__main__":

    if njobs == -1:
        if os.path.exists(local_dir):
            print(f"Please remove test dir {local_dir}")
            quit()
        os.makedirs(local_dir)
        out_dir = local_dir
        sh = make(32768, local_dir)
        os.system('cd %s && %s'%(local_dir, sh))
        
        # extract cross-section
        #os.system('cat %s/job_32768/whizard.log | grep "| Time estimate for generating" -B 3'%local_dir)
    else:
        if not os.path.exists(submit_dir):
            os.makedirs(submit_dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    
        execs = []
        njob = 0
        while njob < njobs:
            seed = f"{random.randint(10000,32768)}"
            sh = make(seed, submit_dir)
            if sh == -1:
                continue
            njob += 1
            print(f"Prepare job {njob} with seed {seed}")
            execs.append(sh)
            
        fOutName = f'{submit_dir}/condor.cfg'
        fOut = open(fOutName, 'w')

        fOut.write(f'executable     = $(filename)\n')
        fOut.write(f'Log            = {submit_dir}/condor_job.$(ClusterId).$(ProcId).log\n')
        fOut.write(f'Output         = {submit_dir}/condor_job.$(ClusterId).$(ProcId).out\n')
        fOut.write(f'Error          = {submit_dir}/condor_job.$(ClusterId).$(ProcId).error\n')
        fOut.write(f'getenv         = True\n')
        fOut.write(f'environment    = "LS_SUBCWD={submit_dir}"\n')
        fOut.write(f'requirements   = ( (OpSysAndVer =?= "CentOS7") && (Machine =!= LastRemoteHost) && (TARGET.has_avx2 =?= True) )\n')
   
        fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        fOut.write(f'max_retries    = 3\n')
        fOut.write(f'+JobFlavour    = "{queue}"\n')
        fOut.write(f'+AccountingGroup = "{priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {fOutName}')
        os.system(f"condor_submit {fOutName}")
