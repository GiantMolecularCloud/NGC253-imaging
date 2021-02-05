####################################################################################################

# run regrid task
#################


def regrid_band(MS_file, width, restfreq, phasecenter):

    """
    Regrid an MS to the target velocity structure.
    This way clean() does not have to regrid the data (which produces lots of failues)
    but can simply image every channel.
    Width and rest frequency have to be specified!
    """

    casalog.post("*"*80)
    casalog.post("FUNCTION: REGRID SIDEBAND")
    casalog.post("*"*80)

    casalog.post("*"*80)
    casalog.post("* Regridding "+MS_file+" to ...")
    casalog.post("*"*80)

    ###
    # mstransform crashes with a memory dump for the band 7, 12m data   -> mstransform impossible
    # cvel2 does not work with the band 6 data because of a
    # non-uniform channel setup which is not supported                  -> cvel2 impossible
    # cvel cannot regrid channels by more than a factor of 2            -> cvel impossible
    #
    # solution: average with mstranform or split when necessary, then regrid with mstransform
    #           (cvel as the second step does not work due to "Table DataManager: no array in row 0 of column SIGMA_SPECTRUM")
    ##

    # check if output width larger than a factor of two
    chan_widths = au.getChanWidths(MS_file)
    chan_widths = [abs(ch)*u.Hz for ch in chan_widths]
    chan_widths_kms = [(ch/u.Quantity(restfreq)*c.c).to(u.km/u.s) for ch in chan_widths]

    # merge channels prior to regridding to avoid problems with cvel
    if (min(chan_widths) <= 0.5*u.Quantity(width)):
        casalog.post("*"*80)
        casalog.post("* Target channel width >2 input channel width. Need an intermediate step because of bugs in cvel/cvel2/mstransform.")
        casalog.post("* channel width: "+str(min(chan_widths))+"     target width: "+str(width))
        casalog.post("*"*80)

        # merge channels
        mstransform(vis = MS_file,
            outputvis   = MS_file+'.__temp__',
            datacolumn  = 'data',
            chanaverage = True,
            chanbin     = 2,
            regridms    = False,
            keepflags   = False
            )
        regrid_vis = MS_file+'.__temp__'
    else:
        regrid_vis = MS_file

    # regrid to target resolution
    mstransform(vis = regrid_vis,
        outputvis   = MS_file+'.regrid',
        datacolumn  = 'data',
        spw         = '',
        chanaverage = False,
        regridms    = True,
        combinespws = False,            # does not work
        mode          = 'frequency',
        nchan         = -1,
        start         = 0,
        width         = width,
        interpolation = 'linear',
        phasecenter   = phasecenter,
        restfreq      = restfreq,
        outframe      = 'LSRK',
        veltype       = 'radio',        # use radio because casa always uses radio internally
        hanning       = False
        )

    # get listobs info
    listobs(vis    = MS_file+'.regrid',
        selectdata = False,
        listfile   = MS_file+'.regrid.listobs'
        )


####################################################################################################
