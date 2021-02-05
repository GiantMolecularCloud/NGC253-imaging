####################################################################################################

# dirty image
#############

def dirty_image(MS_file):

    casalog.post("*"*80)
    casalog.post("FUNCTION: DIRTY IMAGE")
    casalog.post("*"*80)

    # The tclean task depends on certain casa versions.
    is_casa_version('5.5.0-31')

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)

    # run unconstrained clean to get beam size
    os.system('mkdir -p '+os.path.join(imagedir, subdir))
    tclean(vis            = os.path.join(imagedir,'visdir',MS_file),
           selectdata     = False,
           datacolumn     = 'data',
           imagename      = imbasename+'.dirty',
           imsize         = imsize,
           cell           = str(cell),
           phasecenter    = phasecenter,
           specmode       = 'cube',
           nchan          = -1,
           start          = '',
           width          = 1,
           outframe       = 'LSRK',
           veltype        = 'optical',
           restfreq       = str(restfreq),
           interpolation  = 'linear',
           gridder        = 'mosaic',
           chanchunks     = 1,
           mosweight      = True,
           pblimit        = 0.1,
           deconvolver    = 'multiscale',
           scales         = [0,3,9,27,81],
           smallscalebias = 0.6,
           restoration    = True,
           restoringbeam  = [],
           pbcor          = False,
           weighting      = 'briggs',
           robust         = 0.5,
           niter          = 0,
           gain           = 0.1,
           threshold      = str(0.0*noise),
           usemask        = 'user',
           mask           = '',
           restart        = True,
           calcres        = True,
           calcpsf        = True
           )

    casalog.post("*"*80)
    casalog.post("FINISHED DIRTY IMAGE")
    casalog.post("*"*80)


####################################################################################################
