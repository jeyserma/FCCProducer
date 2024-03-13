
import sys, os, glob, shutil
import time
import argparse
import pathlib
import json
import logging
import config
import subprocess
import random
import numpy as np
import fccproducer

logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger("fcclogger")
logger.setLevel(logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument("--submit", action='store_true', help="Submit grid")
parser.add_argument("--check", action='store_true', help="Check step")
'''
parser.add_argument("-s", "--submit", action='store_true', help="Submit to batch system")
parser.add_argument("-n", "--nevents", type=int, help="number of events", default=100)
parser.add_argument("-j", "--njobs", type=int, help="number of jobs", default=10)
parser.add_argument("-p", "--process", type=str, help="Process name", default="p8_ee_Z_ecm91p2")
parser.add_argument("-d", "--detector", type=str, help="Detector name", default="IDEA")
parser.add_argument("-c", "--campaign", type=str, help="Campaign name", default="winter2023")
parser.add_argument("--condor_queue", type=str, help="Condor priority", choices=["espresso", "microcentury", "longlunch", "workday", "tomorrow", "testmatch", "nextweek"], default="workday")
parser.add_argument("--condor_priority", type=str, help="Condor priority", default="group_u_FCC.local_gen")
parser.add_argument("--storagedir", type=str, help="Base directory to save the samples", default="/eos/experiment/fcc/users/j/jaeyserm/sampleProduction2024")



# yfsww parms
parser.add_argument("--ecm", type=float, help="Center-of-mass energy (GeV)", default=163)
parser.add_argument("--mw", type=float, help="W boson mass (MeV)", default=80379) # pdg22 80.377 pm 0.012
parser.add_argument("--ww", type=float, help="W boson width (MeV)", default=2085) # pdg22 2.085 pm 0.042
'''
args = parser.parse_args()




if __name__ == "__main__":
    process = "yfsww_ee_ww_noBES"
    ecms = list(np.arange(155, 171, 1))
    mws = list(np.arange(-10, 10.5, 0.5))
    mws = [80359, 80369, 80379, 80389, 80399]
    mws = [80359, 80369, 80389, 80399]
    #mws = [80379]
    #print(ecms)
    #print(mws)
    #print(len(ecms), len(mws))
    
    # yfsww_ee_ww_noBES_ecm169_minus10MeV
    basedir = "submit/winter2023/IDEA"
    
    #cmd = ['grep', '-R', 'XPAR', 'submit/winter2023/IDEA/yfsww_ee_ww_noBES_ecm155_plus20MeV/', '|', 'awk', ' -F \' \'', '\'{print $2}\'']
    #print(' '.join(cmd))
    #cmd = ' '.join(cmd)
    #result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    #print(result)
    
    
    #quit()
    target_jobs = 100
    nevents_per_job = 100000
    
    for ecm in ecms:
        for mw in mws:
            njobs = 0
            ext = f"mw{mw}"
            dir_ = f"{basedir}/{process}_ecm{ecm}_{ext}"
            if os.path.isdir(dir_):
                cmd = f"grep -R XPAR {dir_} --include \*.out | awk -F ' ' '{{print $2 \" \" $4}}'"
                result = subprocess.check_output(cmd, shell=True, universal_newlines=True).splitlines()
                njobs = target_jobs - len(result)
            else:
                njobs = target_jobs
            if njobs <= 0:
                continue
            cmd = f"python python/submit.py -p {process} --nevents {nevents_per_job} --skipDelphes --submit --njobs {njobs} --ecm {ecm} --mw {mw} --ext {ext}"
            print(cmd)
            if args.submit:
                os.system(cmd)
    
    #if args.check:
        
    
    
    #80379
    
    
    args.skipDelphes = True
    args.ecm = 163
    args.mw = 80379
    args.ww = 2085
    
    #producer = fccproducer.FCCProducer(process, "winter2023", "IDEA", "/tmp", args)
    #producer.generate_local(run=True, nevents=1000000)

