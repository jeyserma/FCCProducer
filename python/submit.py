
import sys
import os
import datetime
import config
import functions


parser = functions.common_parser()
parser.add_argument('--nEvents', type=int, help='Number of events per job', default=100)
parser.add_argument('--nJobs', type=int, default = 10, help='Number of jobs')
parser.add_argument('-q', '--queue', type=str, default='longlunch', help='Condor queue', choices=['espresso','microcentury','longlunch','workday','tomorrow','testmatch','nextweek'])
args = parser.parse_args()
    


def submit():

    rundir = f"{os.getcwd()}/submit/{args.tag}/{args.process}_{args.type}"
    if not os.path.exists(rundir):
        os.makedirs(rundir)

    generator = functions.get_generator(args.process)
    
    execs = [] 
    if args.type == "gen":
    
        outDir = f'{config.gen_dir}/{args.tag}/{args.process}/'
        if not os.path.exists(outDir):
            os.makedirs(outDir)
    
        baseId = int(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
        for iJob in range(0, args.nJobs):
            jobId = int(f"{baseId}{iJob}")
            jobName = functions.prepare_job(jobId, generator, args.tag, args.process, rundir, outDir, nEvents=args.nEvents)
            execs.append(jobName)

        functions.submit_condor(rundir, execs, args.queue)
        
        fOut = open(f'{outDir}/stat_{baseId}.txt', 'w')
        fOut.write(f'nJobs={args.nJobs}\n')
        fOut.write(f'nEvents={args.nEvents}\n')
        fOut.close()
        
    elif args.type == "reco":
    
        outDir = f'{config.reco_dir}/{args.tag}/{args.process}/'
        if not os.path.exists(outDir):
            os.makedirs(outDir)
    
        if generator == "whizard":
        
            stdhep_dir = f'{config.gen_dir}/{args.tag}/{args.process}/'
            reco_file_ids = functions.get_file_ids(outDir)
            stdhep_file_ids = functions.get_file_ids(stdhep_dir)

            print(f'Found {len(stdhep_file_ids)} stdhep files, {len(reco_file_ids)} reco files. Will process remaining {len(stdhep_file_ids)-len(reco_file_ids)} stdhep files')
            ids = list(set(stdhep_file_ids).difference(set(reco_file_ids)))
        
    elif args.type == "gen_reco":
        pass

if __name__=="__main__":


    submit()


