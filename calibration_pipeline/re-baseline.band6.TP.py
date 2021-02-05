####################################################################################################

# re-baselining all TP datasets
###############################

# This scripts documents a lot of manual work, especially looking at a lot of images to check if
# they look correct.

####################################################################################################

# rename to get handlable names
os.system('for i in `ls | grep .ms.cal.jy`; do mv $i ${i:19}; done')

# initial files to processes
pipeline_vis = glob.glob('*.ms.cal.jy')


####################################################################################################

# split into spws and image
###########################

for TP_vis in pipeline_vis:
    science_spws = au.getScienceSpws(TP_vis)
    science_spws = science_spws.split(',')

    for science_spw in science_spws:
        split(vis      = TP_vis,
            spw        = science_spw,
            outputvis  = TP_vis+'.spw'+science_spw,
            datacolumn = 'float_data',
            width      = 1
            )
        sdimaging(infiles = TP_vis+'.spw'+science_spw,
            outfile = TP_vis+'.spw'+science_spw+'.image',
            spw     = '',
            mode    = 'channel',
            nchan   = -1,
            start   = '',
            width   = 1,
            veltype = 'optical',
            outframe     = 'LSRK',
            restfreq     = '',
            gridfunction = 'SF',          # recommended for ALMA
            convsupport  = 6,             # recommended for ALMA
            imsize       = 64,
            cell         = '5.0arcsec',
            phasecenter  = ''
            )


####################################################################################################

# check manually which spw needs re-baselining
##############################################

#                  file, spw, line range
rebaseline = [['X1153','19','140~380'],
              ['X1153','25','95~315'],
              ['X1396','19','140~380'],
              ['X1396','25','95~315'],
              ['X1737','19','140~380'],
              ['X1737','25','95~315'],
              ['X1f12','19','140~380'],
              ['X1f12','25','0~30;95~315'],
              ['X265c','19','140~380'],
              ['X265c','25','95~315'],
              ['X29a9','19','140~380'],
              ['X29a9','25','95~315'],
#              ['X2cae','19','0~30;140~380'],    # these are really screwed up, flag out completely
#              ['X2cae','25','0~30;95~315'],     # these are really screwed up, flag out completely
              ['X2fdd','19','0~30;140~380'],
              ['X2fdd','25','0~30;95~315'],
              ['X512c','37','0~30;140~380'],
              ['X512c','43','0~30;95~315'],
              ['X70a9','19','140~380'],
              ['X70a9','25','95~315']]

# subtract baseline and image again
for rebase in rebaseline:
    vis_base = rebase[0]
    inp_spw  = rebase[1]
    lrange   = rebase[2]

    # invert line range to line-free range
    lfrange = au.invertChannelRanges('0:'+lrange, vis=vis_base+'.ms.cal.jy.spw'+inp_spw)

    sdbaseline(infile = vis_base+'.ms.cal.jy.spw'+inp_spw,
        outfile    = vis_base+'.ms.cal.jy.spw'+inp_spw+'.rebaseline',
        datacolumn = 'float_data',
        spw        = lfrange,
        maskmode   = 'list',
        blmode     = 'fit',
        dosubtract = True,
        blformat   = 'text',
        bloutput   = vis_base+'.ms.cal.jy.spw'+inp_spw+'.bloutput',
        blfunc     = 'poly',
        order      = 1,
        clipthresh = 3.0,
        clipniter  = 0,
        overwrite  = True
        )
    sdimaging(infiles = vis_base+'.ms.cal.jy.spw'+inp_spw+'.rebaseline',
        outfile = vis_base+'.ms.cal.jy.spw'+inp_spw+'.rebaseline.image',
        spw     = '',
        mode    = 'channel',
        nchan   = -1,
        start   = '',
        width   = 1,
        veltype = 'optical',
        outframe     = 'LSRK',
        restfreq     = '',
        gridfunction = 'SF',          # recommended for ALMA
        convsupport  = 6,             # recommended for ALMA
        imsize       = 64,
        cell         = '5.0arcsec',
        phasecenter  = ''
        )


####################################################################################################

# manual adjustments
####################

# flag bad edges
flagdata(vis = 'X2fdd.ms.cal.jy.spw25.rebaseline',
    mode     = 'manual',
    spw      = '0:0~20',
    action   = 'apply',
    flagbackup = True
    )
flagdata(vis = 'X29a9.ms.cal.jy.spw25.rebaseline',
    mode     = 'manual',
    spw      = '0:0~20',
    action   = 'apply',
    flagbackup = True
    )
flagdata(vis = 'X1737.ms.cal.jy.spw25.rebaseline',
    mode     = 'manual',
    spw      = '0:110~160',
    action   = 'apply',
    flagbackup = True
    )


####################################################################################################

# concat sidebands of each dataset
##################################

vis_bases = [x.split('.')[0] for x in glob.glob('*.ms.cal.jy')]
for vis_base in vis_bases:

    casalog.post("*"*80)
    casalog.post("Concatenating "+vis_base)
    casalog.post("*"*80)

    # sort out which files to concat
    all_vis = sorted(glob.glob(vis_base+'.ms.cal.jy.spw??') + glob.glob(vis_base+'.ms.cal.jy.spw??.rebaseline'))
    for vis in all_vis:
        if ( 'rebaseline' in vis ):
            spw = vis.split('.')[4]
            for idx,i in enumerate(all_vis):
                if ( spw in i ) and not ( 'rebaseline' in i ):
                    del all_vis[idx]

    lsb_vis = sorted(all_vis)[:3]
    usb_vis = sorted(all_vis)[3:]

    concat(vis       = lsb_vis,
        concatvis    = vis_base+'.ms.cal.jy.rebaseline.concat.LSB',
        copypointing = True,
        freqtol      = ''
        )
    concat(vis       = usb_vis,
        concatvis    = vis_base+'.ms.cal.jy.rebaseline.concat.USB',
        copypointing = True,
        freqtol      = ''
        )

# X2cae spw 19 and 25 are unusable
os.system('rm -rf X2cae.ms.cal.jy.rebaseline.concat.?SB')
concat(vis       = ['X2cae.ms.cal.jy.spw17','X2cae.ms.cal.jy.spw21'],
    concatvis    = 'X2cae.ms.cal.jy.rebaseline.concat.LSB',
    copypointing = True,
    freqtol      = ''
    )
concat(vis       = ['X2cae.ms.cal.jy.spw23','X2cae.ms.cal.jy.spw27'],
    concatvis    = 'X2cae.ms.cal.jy.rebaseline.concat.USB',
    copypointing = True,
    freqtol      = ''
    )

# check if each dataset is ok
all_vis = glob.glob('*.ms.cal.jy.rebaseline.concat.LSB') + glob.glob('*.ms.cal.jy.rebaseline.concat.USB')
for vis in all_vis:
    sdimaging(infiles = vis,
        outfile = vis+'.image',
        spw     = '',
        mode    = 'channel',
        nchan   = -1,
        start   = '',
        width   = 1,
        veltype = 'optical',
        outframe     = 'LSRK',
        restfreq     = '',
        gridfunction = 'SF',          # recommended for ALMA
        convsupport  = 6,             # recommended for ALMA
        imsize       = 64,
        cell         = '5.0arcsec',
        phasecenter  = ''
        )


####################################################################################################

# concat all datasets
#####################

lsb_vis = glob.glob('*.ms.cal.jy.rebaseline.concat.LSB')
usb_vis = glob.glob('*.ms.cal.jy.rebaseline.concat.USB')
concat(vis       = lsb_vis,
    concatvis    = 'NGC253.band6.TP.LSB',
    copypointing = True,
    freqtol      = ''
    )
concat(vis       = usb_vis,
    concatvis    = 'NGC253.band6.TP.USB',
    copypointing = True,
    freqtol      = ''
    )

sdimaging(infiles = 'NGC253.band6.TP.LSB',
    outfile = 'NGC253.band6.TP.LSB.image',
    spw     = '',
    mode    = 'channel',
    nchan   = -1,
    start   = '',
    width   = 1,
    veltype = 'optical',
    outframe     = 'LSRK',
    restfreq     = '',
    gridfunction = 'SF',          # recommended for ALMA
    convsupport  = 6,             # recommended for ALMA
    imsize       = 64,
    cell         = '5.0arcsec',
    phasecenter  = ''
    )
sdimaging(infiles = 'NGC253.band6.TP.USB',
    outfile = 'NGC253.band6.TP.USB.image',
    spw     = '',
    mode    = 'channel',
    nchan   = -1,
    start   = '',
    width   = 1,
    veltype = 'optical',
    outframe     = 'LSRK',
    restfreq     = '',
    gridfunction = 'SF',          # recommended for ALMA
    convsupport  = 6,             # recommended for ALMA
    imsize       = 64,
    cell         = '5.0arcsec',
    phasecenter  = ''
    )


####################################################################################################

# regrid to final channel width
###############################

# THIS CREATES CORRUPTED MS FILES !!!

# execfile('NGC253/project_info.py')
# lsb_idx = get_idx(datasets, 'NGC253.band6.TP.ms.LSB')
# usb_idx = get_idx(datasets, 'NGC253.band6.TP.ms.USB')
#
# mstransform(vis = 'NGC253.band6.TP.LSB',
#     outputvis   = 'NGC253.band6.TP.LSB.regrid',
#     datacolumn  = 'float_data',
#     spw         = '',
#     chanaverage = False,
#     regridms    = True,
#     combinespws = False,            # does not work
#     mode          = 'frequency',
#     nchan         = -1,
#     start         = 0,
#     width         = datasets[lsb_idx]['width'],
#     interpolation = 'linear',
#     phasecenter   = phasecenter,
#     restfreq      = datasets[lsb_idx]['restfreq'],
#     outframe      = 'LSRK',
#     veltype       = 'radio',        # use radio because casa always uses radio internally
#     hanning       = False
#     )
# mstransform(vis = 'NGC253.band6.TP.USB',
#     outputvis   = 'NGC253.band6.TP.USB.regrid',
#     datacolumn  = 'float_data',
#     spw         = '',
#     chanaverage = False,
#     regridms    = True,
#     combinespws = False,            # does not work
#     mode          = 'frequency',
#     nchan         = -1,
#     start         = 0,
#     width         = datasets[usb_idx]['width'],
#     interpolation = 'linear',
#     phasecenter   = phasecenter,
#     restfreq      = datasets[usb_idx]['restfreq'],
#     outframe      = 'LSRK',
#     veltype       = 'radio',        # use radio because casa always uses radio internally
#     hanning       = False
#     )


####################################################################################################
