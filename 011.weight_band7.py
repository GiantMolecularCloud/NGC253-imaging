####################################################################################################
# CASA MS PREPARATION PIPELINE
####################################################################################################

# import modules
################

interactive = False
import shlex
from subprocess import check_output
execfile('scripts/plotting_imports.py')
execfile('scripts/casa_scripts/execute_casa_parallel.py')


####################################################################################################

# load project info
###################

execfile('NGC253/project_info.py')


####################################################################################################

# correct weights
#################

processes = []
for band in ['.band7']:
    for array in ['.ACA','.12m-mid','.12m-high']:
        for sideband in ['.LSB', '.USB']:
            for cont in ['.contsub', '']:

                vis = 'NGC253'+band+array+'.ms'+sideband+cont
                dataset = datasets[get_idx(datasets, 'NGC253'+band+array+'.ms'+sideband)]

                tmp_dict = {'name': vis, 'process': 0, 'status': 'not started'}
                task = 'casa-5.3.0-140 --nologger'
                task += ' --logfile '+os.path.join(logdir,vis+'.statwt.log')
                task += ' -c "execfile(\'scripts/NGC253/001.calibration_pipeline/correct_weights.py\')'
                task += '; execfile(\'scripts/casa_scripts/expand_spw_string.py\')'
                task += '; os.system(\'cp -r '+vis+' '+vis+'.statwt\')'
                task += '; correct_weights(\''+os.path.join(datadir,vis+'.statwt')+'\',\''+dataset['linefree']+'\')"'
                tmp_dict['task'] = shlex.split(task)
                processes.append(tmp_dict)

# run statwt tasks
casa_execute_parallel(processes, max_threads=12)


####################################################################################################

# concat arrays
###############

# This cannot be fully parallelized because casa writes a lock file.
# Several steps, however can run in parallel.

processes = []
for band in ['.band7']:
    for sideband in ['.LSB', '.USB']:
        for cont in ['.contsub', '']:
            tmp_dict = {'name': 'concat '+band+sideband+cont, 'process': 0, 'status': 'not started'}
            task = 'casa-5.3.0-140 --nologger'
            task += ' --logfile '+os.path.join(logdir,'NGC253'+band+sideband+cont+'.statwt.concat.log')
            task += ' -c "'
            task += 'concat(vis = [\'NGC253'+band+'.ACA.ms'+sideband+cont+'.statwt\', \'NGC253'+band+'.12m-mid.ms'+sideband+cont+'.statwt\'], concatvis = \'NGC253'+band+'.ACA+12m-mid.ms'+sideband+cont+'.statwt\', freqtol = \'\', copypointing = False); '
            task += 'concat(vis = [\'NGC253'+band+'.12m-mid.ms'+sideband+cont+'.statwt\', \'NGC253'+band+'.12m-high.ms'+sideband+cont+'.statwt\'], concatvis = \'NGC253'+band+'.12m-mid+12m-high.ms'+sideband+cont+'.statwt\', freqtol = \'\', copypointing = False); '
            task += 'concat(vis = [\'NGC253'+band+'.ACA+12m-mid.ms'+sideband+cont+'.statwt\', \'NGC253'+band+'.12m-high.ms'+sideband+cont+'.statwt\'], concatvis = \'NGC253'+band+'.ACA+12m-mid+12m-high.ms'+sideband+cont+'.statwt\', freqtol = \'\', copypointing = False); '
            task += '"'
            tmp_dict['task'] = shlex.split(task)
            processes.append(tmp_dict)

# run concat tasks
casa_execute_parallel(processes, max_threads=10)

# check file size
arrays = ['ACA', '12m-mid', '12m-high', 'ACA+12m-mid', '12m-mid+12m-high', 'ACA+12m-mid+12m-high']
for band in ['.band7']:
    for sideband in ['.LSB', '.USB']:
        for cont in ['.contsub', '']:
            sizes = []
            for array in arrays:
                try:
                    sizes.append(check_output('du -sh NGC253'+band+'.'+array+'.ms'+sideband+cont+".statwt | awk '{print $1}'", shell=True)[:-1])
                except:
                    sizes.append('-')
            print("\n"+band+sideband+cont)
            print("\t".join(arrays))
            print("\t".join(sizes))


####################################################################################################

# regrid bands
##############

processes = []
for dataset in all_datasets_contsub:
    if 'band7' in dataset['name']:
        if not 'TP' in dataset['name']:
            tmp_dict = {'name': dataset['name']+'.statwt', 'process': 0, 'status': 'not started'}
            task = 'casa-5.3.0-140 --nologger'
            task += ' --logfile '+os.path.join(logdir,dataset['name']+'.statwt.regrid.log')
            task += ' -c "execfile(\'scripts/NGC253/001.calibration_pipeline/regrid_band.py\')'
            task += '; regrid_band(\''+os.path.join(datadir,dataset['name']+'.statwt')+'\', width=\''+dataset['width']+'\', restfreq=\''+dataset['restfreq']+'\', phasecenter=\''+phasecenter+'\')"'
            tmp_dict['task'] = shlex.split(task)
            processes.append(tmp_dict)

# run regridding task
casa_execute_parallel(processes, max_threads=10)


####################################################################################################
