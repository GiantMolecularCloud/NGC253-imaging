####################################################################################################
# CASA MS PREPARATION PIPELINE
####################################################################################################

# import modules
################

import shlex
from subprocess import check_output
execfile('scripts/plotting_imports.py')
execfile('scripts/casa_scripts/execute_casa_parallel.py')


####################################################################################################

# load project info
###################

execfile('NGC253/project_info.py')


####################################################################################################

# ask which task should be executed
###################################

print("Which steps should be executed? Multiple are possible. These are available:")
for step in ["listobs","split_sidebands","merge_spws", "correct_weights", "contsub","concat","regrid_bands","split_chunks"]:
    print("\t"+step)
steps = raw_input("Step? ")

####################################################################################################

# get datasets
####################################

# This has to be done manually:
# The source is split out from the delivered MS and renamed in a meaningful way. These names and dataset
# properties are listed in project_info.py as a dictionary in the variable datasets.


####################################################################################################

# get listobs for all files (test parallelisation)
##################################################

if "listobs" in steps:
    processes = []
    for raw_dataset in raw_datasets:
        tmp_dict = {'name': raw_dataset['name'], 'process': 0, 'status': 'not started'}
        task = 'casa --nologger'
        task += ' --logfile '+logdir+raw_dataset['name']+'.listobs.log'
        task += ' -c "listobs(vis=\''+datadir+raw_dataset['name']+'\',selectdata=False,listfile=\''+datadir+raw_dataset['name']+'.listobs\')"'
        tmp_dict['task'] = shlex.split(task)
        processes.append(tmp_dict)

    # run listobs tasks
    casa_execute_parallel(processes, max_threads=10)


####################################################################################################

# split sidebands
#################

if "split_sidebands" in steps:
    processes = []
    for raw_dataset in raw_datasets:
        tmp_dict = {'name': raw_dataset['name'], 'process': 0, 'status': 'not started'}
        task = 'casa --nologger'
        task += ' --logfile '+logdir+raw_dataset['name']+'.split_sidebands.log'
        task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/split_sidebands.py\')'
        task += '; split_sidebands(\''+datadir+raw_dataset['name']+'\')"'
        tmp_dict['task'] = shlex.split(task)
        processes.append(tmp_dict)

    # run splitting tasks
    casa_execute_parallel(processes, max_threads=10)


####################################################################################################

# merge spws
############

if "merge_spws" in steps:
    print("merging spws does not work for this project!")
#     processes = []
#     for dataset in datasets:
#         tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
#         task = 'casa --nologger'
#         task += ' --logfile '+logdir+dataset['name']+'.merge.log'
#         task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/merge_spws.py\')'
#         task += '; merge_spws(\''+datadir+dataset['name']+'\', restfreq=\''+dataset['restfreq']+'\', phasecenter=\''+phasecenter+'\')"'
#         tmp_dict['task'] = shlex.split(task)
#         processes.append(tmp_dict)
#
#     # run splitting task
#     casa_execute_parallel(processes, max_threads=10)


####################################################################################################

# correct weights
#################

if "correct_weights" in steps:
    processes = []
    for dataset in datasets:
        if 'band6' in dataset['name']:
            tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
            task = 'casa --nologger'
            task += ' --logfile '+logdir+dataset['name']+'.statwt.log'
            task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/correct_weights.py\')'
            task += '; execfile(\'scripts/casa_scripts/expand_spw_string.py\')'
            task += '; correct_weights(\''+datadir+dataset['name']+'\',\''+dataset['linefree']+'\')"'
            tmp_dict['task'] = shlex.split(task)
            processes.append(tmp_dict)

    # run statwt tasks
    casa_execute_parallel(processes, max_threads=10)


####################################################################################################

# subtract continuum
####################

if "contsub" in steps:
    processes = []
    for dataset in datasets:
        tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
        task = 'casa --nologger'
        task += ' --logfile '+logdir+dataset['name']+'.contsub.log'
        task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/subtract_continuum.py\')'
        task += '; subtract_continuum(\''+datadir+dataset['name']+'\',\''+dataset['linefree']+'\')"'
        tmp_dict['task'] = shlex.split(task)
        processes.append(tmp_dict)

    # run contsub tasks
    casa_execute_parallel(processes, max_threads=10)


####################################################################################################

# concat arrays
###############

# This cannot be fully parallelized because casa writes a lock file.
# Several steps, however can run in parallel.

if "concat" in steps:
    processes = []
    for band in ['.band6', '.band7']:
        for sideband in ['.LSB', '.USB']:
            for cont in ['.contsub', '']:
                tmp_dict = {'name': 'concat '+band+sideband+cont, 'process': 0, 'status': 'not started'}
                task = 'casa --nologger'
                task += ' --logfile '+logdir+'NGC253'+band+sideband+cont+'.concat.log'
                task += ' -c "'
                task += 'concat(vis = [\'NGC253'+band+'.ACA.ms'+sideband+cont+'\', \'NGC253'+band+'.12m-mid.ms'+sideband+cont+'\'], concatvis = \'NGC253'+band+'.ACA+12m-mid.ms'+sideband+cont+'\', freqtol = \'\', copypointing = False); '
                task += 'concat(vis = [\'NGC253'+band+'.12m-mid.ms'+sideband+cont+'\', \'NGC253'+band+'.12m-high.ms'+sideband+cont+'\'], concatvis = \'NGC253'+band+'.12m-mid+12m-high.ms'+sideband+cont+'\', freqtol = \'\', copypointing = False); '
                task += 'concat(vis = [\'NGC253'+band+'.ACA+12m-mid.ms'+sideband+cont+'\', \'NGC253'+band+'.12m-high.ms'+sideband+cont+'\'], concatvis = \'NGC253'+band+'.ACA+12m-mid+12m-high.ms'+sideband+cont+'\', freqtol = \'\', copypointing = False); '
                task += '"'
                tmp_dict['task'] = shlex.split(task)
                processes.append(tmp_dict)

    # run concat tasks
    casa_execute_parallel(processes, max_threads=10)

    # check file size
    arrays = ['ACA', '12m-mid', '12m-high', 'ACA+12m-mid', '12m-mid+12m-high', 'ACA+12m-mid+12m-high']
    for band in ['.band6', '.band7']:
        for sideband in ['.LSB', '.USB']:
            for cont in ['.contsub', '']:
                sizes = []
                for array in arrays:
                    try:
                        sizes.append(check_output('du -sh NGC253'+band+'.'+array+'.ms'+sideband+cont+" | awk '{print $1}'", shell=True)[:-1])
                    except:
                        sizes.append('-')
                print("\n"+band+sideband+cont)
                print("\t".join(arrays))
                print("\t".join(sizes))


####################################################################################################

# regrid bands
##############

if "regrid_bands" in steps:
    processes = []
    # for dataset in all_datasets_cont:
    #     tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
    #     task = 'casa --nologger'
    #     task += ' --logfile '+logdir+dataset['name']+'.regrid.log'
    #     task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/regrid_band.py\')'
    #     task += '; regrid_band(\''+datadir+dataset['name']+'\', width=\''+dataset['width']+'\', restfreq=\''+dataset['restfreq']+'\', phasecenter=\''+phasecenter+'\')"'
    #     tmp_dict['task'] = shlex.split(task)
    #     processes.append(tmp_dict)
    for dataset in all_datasets_contsub:
        tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
        task = 'casa --nologger'
        task += ' --logfile '+logdir+dataset['name']+'.regrid.log'
        task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/regrid_band.py\')'
        task += '; regrid_band(\''+datadir+dataset['name']+'\', width=\''+dataset['width']+'\', restfreq=\''+dataset['restfreq']+'\', phasecenter=\''+phasecenter+'\')"'
        tmp_dict['task'] = shlex.split(task)
        processes.append(tmp_dict)

    # run splitting task
    casa_execute_parallel(processes, max_threads=10)


####################################################################################################

# split into chunks
###################

if "split_chunks" in steps:
    print("Splitting into chunks only works when spws are merged!")

    # processes = []
    # # for dataset in all_datasets_cont_regrid:
    # #     tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
    # #     task = 'casa --nologger'
    # #     task += ' --logfile '+logdir+dataset['name']+'.regrid.log'
    # #     task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/split_chunks.py\')'
    # #     task += '; split_chunks(\''+datadir+dataset['name']+'\', chunksize=100)"'
    # #     tmp_dict['task'] = shlex.split(task)
    # #     processes.append(tmp_dict)
    # for dataset in all_datasets_contsub_regrid:
    #     tmp_dict = {'name': dataset['name'], 'process': 0, 'status': 'not started'}
    #     task = 'casa --nologger'
    #     task += ' --logfile '+logdir+dataset['name']+'.split_chunks.log'
    #     task += ' -c "execfile(\'scripts/NGC253/calibration_pipeline/split_chunks.py\')'
    #     task += '; split_chunks(\''+datadir+dataset['name']+'\', chunksize=100)"'
    #     tmp_dict['task'] = shlex.split(task)
    #     processes.append(tmp_dict)
    #
    # casa_execute_parallel(processes, max_threads=10)
    #
    # # move chunks to splitdir to keep the datadir directory organized
    # os.system('mv '+datadir+'*.chunk_* '+splitdir)


####################################################################################################
