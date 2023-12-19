
import sys
import os
import config
import functions


parser = functions.common_parser()
parser.add_argument('--nEvents', type=int, help='Number of events per job', default=10000)
parser.add_argument('--nJobs', type=int, default = 10, help='Number of jobs')
parser.add_argument('-q', '--queue', type=str, default='workday', help='HTCONDOR queue', choices=['espresso','microcentury','longlunch','workday','tomorrow','testmatch','nextweek'])
args = parser.parse_args()

    

def run_local():

    rundir = f"local/{args.tag}/{args.process}/"
    
    if os.path.exists(rundir):
        raise Exception(f"Local rundir {rundir} exists")
    os.makedirs(rundir)

    generator = functions.get_generator(args.process)
    
    
    if args.type == "gen":
        functions.parse_card(generator, args.tag, args.process, rundir, run=True)



if __name__=="__main__":


    run_local()


