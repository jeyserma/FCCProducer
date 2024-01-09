
import sys, os, glob, shutil
import time
import argparse
import pathlib
import json
import logging
import config
import subprocess

logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger("fcclogger")
logger.setLevel(logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--submit", action='store_true', help="Submit to batch system")
parser.add_argument("-n", "--nevents", type=int, help="number of events", default=100)
parser.add_argument("-j", "--jobs", type=int, help="number of jobs", default=10)
parser.add_argument("-p", "--process", type=str, help="Process name", default="p8_ee_Z_ecm91p2")
parser.add_argument("-d", "--detector", type=str, help="Detector name", default="IDEA")
parser.add_argument("-c", "--campaign", type=str, help="Campaign name", default="winter2023")
parser.add_argument("--queue", type=str, help="Condor priority", choices=["espresso", "microcentury", "longlunch", "workday", "tomorrow", "testmatch", "nextweek"], default="espresso")
parser.add_argument("--condor_priority", type=str, help="Condor priority", default="group_u_FCC.local_gen")
args = parser.parse_args()




def make(seed, stack, submit_dir, save_dir, process_card, delphes_card, delphes_card_edm4hep, process_module, args):
    
    fOutName = f"{submit_dir}/submit_{seed}.sh"
    if os.path.exists(fOutName):
        return -1
    rootOutName = f"events_{seed}.root"
    if os.path.exists(f"{save_dir}/{rootOutName}"):
        return -1

    fOut = open(fOutName, "w")

    fOut.write("#!/bin/bash\n")
    fOut.write("SECONDS=0\n")
    fOut.write("unset LD_LIBRARY_PATH\n")
    fOut.write("unset PYTHONHOME\n")
    fOut.write("unset PYTHONPATH\n")
    fOut.write(f"mkdir job_{seed}\n")
    fOut.write(f"cd job_{seed}\n")
    fOut.write(f"source {stack}\n")

    # parse the processing card
    if process_module.generator == "p8":
        pythia_card = process_module.cfg.format(seed, args.nevents)
        fOut.write(f"echo \"{pythia_card}\" > card.cmd\n")

    # run PythiaDelphes and produce edm4hep
    fOut.write("echo \"Run PythiaDelphes\"\n")
    fOut.write(f"cp {delphes_card} card.tcl\n")
    fOut.write(f"cp {delphes_card_edm4hep} edm4hep_output_config.tcl\n")

    fOut.write(f"DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd {rootOutName}\n")
    fOut.write("echo \"DONE\"\n")

    fOut.write("echo \"Copy file\"\n")
    fOut.write(f"cp {rootOutName} {save_dir}/\n")

    fOut.write("duration=$SECONDS\n")
    fOut.write("echo \"Duration: $(($duration))\"\n")
    fOut.write(f"echo \"Events: {args.nevents}\"\n")

    subprocess.getstatusoutput(f"chmod 777 {fOutName}")
    return fOutName


def main():

    campaign = args.campaign
    process = args.process
    detector = args.detector
    generator = process.split("_")[0]

    cwd = os.getcwd()
    stack = config.stacks[campaign]

    process_card = f"{cwd}/cards/{campaign}/generator/{generator}/{process}.py"
    delphes_card = f"{cwd}/cards/{campaign}/delphes/card_{detector}.tcl"
    delphes_card_edm4hep = f"{cwd}/cards/{campaign}/delphes/edm4hep_{detector}.tcl"

    sys.path.insert(0, os.path.dirname(process_card))
    process_module = __import__(process)

    submit_dir = f"{cwd}/submit/{campaign}/{process}/"
    out_dir = f"/eos/experiment/fcc/users/j/jaeyserm/sampleProduction/{campaign}/{process}/"
    local_dir = f"{cwd}/local/{campaign}/{process}/"

    if args.submit:
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
        fOut.write(f'+JobFlavour    = "{args.queue}"\n')
        fOut.write(f'+AccountingGroup = "{args.condor_priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {fOutName}')
        os.system(f"condor_submit {fOutName}")

    else:
        if os.path.exists(local_dir):
            logger.error(f"Please remove test dir {local_dir}")
            sys.exit(1)
        os.makedirs(local_dir)
        out_dir = local_dir
        sh = make(32769, stack, local_dir, local_dir, process_card, delphes_card, delphes_card_edm4hep, process_module, args)
        os.system(f"cd {local_dir} && {sh}")


if __name__ == "__main__":
    main()