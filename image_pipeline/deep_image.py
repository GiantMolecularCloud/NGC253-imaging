####################################################################################################

# deep image
############

def deep_image(MS_file, data_range_known=False):

    casalog.post("*"*80)
    casalog.post("FUNCTION: DEEP IMAGE")
    casalog.post("*"*80)

    # The tclean task depends on certain casa versions.
#    is_casa_version('5.5.0-31')

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)
    badchans   = image_setups[get_idx(image_setups, MS_file, key='MS')]['bad chans']
    start,end  = image_setups[get_idx(image_setups, MS_file, key='MS')]['data range']

    # run a new clean with fixed beam
    # Casa does not accept masks of the correct shape, so a first clean run has to create a mask
    # that is then altered and a second clean run does the actual cleaning.
    tclean(vis            = os.path.join(imagedir,'visdir',MS_file),
           selectdata     = False,
           datacolumn     = 'data',
           imagename      = imbasename+'.deep',
           imsize         = imsize,
           cell           = str(cell),
           phasecenter    = phasecenter,
           specmode       = 'cube',
           nchan          = end-start,
           start          = start,
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
           restoringbeam  = [str(major),str(minor),str(pa)],
           pbcor          = False,
           weighting      = 'briggs',
           robust         = 0.5,
           niter          = 1,
           gain           = 0.1,
           threshold      = str(2.5*noise),
           usemask        = 'user',
           mask           = os.path.join(imagedir,subdir,'masks','combined.mask'),
           restart        = True,
           calcres        = True,
           calcpsf        = True
           )

    if not data_range_known:
        # specify channels that need to be masked
        casalog.post("*"*80)
        casalog.post("Check the deep image for bad channels that need to be flagged and specify them in project_info.py")
        casalog.post("*"*80)
        _ = raw_input("\nPress enter to continue ...")

        # reload project info to update bad channels
        execfile('NGC253/project_info.py')
        badchans   = image_setups[get_idx(image_setups, MS_file, key='MS')]['bad chans']

    # flag bad channels if necessary
    if not ( badchans == []):
        ia.open(imbasename+'.deep.mask')
        nx,ny,nstokes,nchan = ia.shape()
        for chan in badchans:
            print("\rmasking channel "+str(chan))
            ia.putchunk(pixels = np.full((nx,ny),0), blc=[0,0,0,chan], inc=1, list=True)
        ia.done()
    else:
        print("No bad channels to flag.")


    # clean to 2.5 sigma
    tclean(vis            = os.path.join(imagedir,'visdir',MS_file),
           selectdata     = False,
           datacolumn     = 'data',
           imagename      = imbasename+'.deep',
           imsize         = imsize,
           cell           = str(cell),
           phasecenter    = phasecenter,
           specmode       = 'cube',
           nchan          = end-start,
           start          = start,
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
           restoringbeam  = [str(major),str(minor),str(pa)],
           pbcor          = False,
           weighting      = 'briggs',
           robust         = 0.5,
           niter          = 320000000,
           gain           = 0.1,
           threshold      = str(2.5*noise),
           usemask        = 'user',
           mask           = '',
           restart        = True,
           calcres        = False,
           calcpsf        = False
           )

    casalog.post("*"*80)
    casalog.post("FINISHED DEEP IMAGE")
    casalog.post("*"*80)


####################################################################################################
