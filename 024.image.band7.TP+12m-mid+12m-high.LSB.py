####################################################################################################
# image NGC 253 # band 7 # 12m-mid+12m-high # LSB #
####################################################################################################

execfile('scripts/casa_imports.py')
execfile('scripts/NGC253/image_pipeline/import_pipeline.py')
execfile('NGC253/project_info.py')


####################################################################################################

MS_file  = 'NGC253.band7.12m-mid+12m-high.ms.LSB.contsub.regrid'
steps    = ['feather','convert K','pbcor','cut out','export final']

line_file = os.path.join(projectdir, 'NGC253.lines.txt')


####################################################################################################

casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))


####################################################################################################

# run pipeline
##############

if 'dirty image' in steps:
    dirty_image(MS_file)
if 'clean mask' in steps:
    clean_mask(MS_file, mask_thresh=25, include_failing_regions = False)
if 'deep image' in steps:
    deep_image(MS_file, data_range_known=True)
if 'export fits' in steps:
    export_fits(MS_file)
if 'feather' in steps:
    feather_TP(MS_file)
if 'convert K' in steps:
    convert_K(MS_file)
if 'pbcor' in steps:
    pbcor(MS_file)
if 'cut out' in steps:
    cut_out_images(MS_file)
if 'export final' in steps:
    export_final(MS_file)
if 'split lines' in steps:
    split_lines()


####################################################################################################
