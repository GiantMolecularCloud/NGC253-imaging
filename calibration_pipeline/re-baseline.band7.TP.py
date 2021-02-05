####################################################################################################

# re-baselining all TP datasets
###############################

# This scripts documents a lot of manual work, especially looking at a lot of images to check if
# they look correct.

####################################################################################################

# split into spws and image
###########################

science_spws = au.getScienceSpws('NGC253.band7.TP.ms')
science_spws = science_spws.split(',')

for science_spw in science_spws:
    split(vis      = 'NGC253.band7.TP.ms',
        spw        = science_spw,
        outputvis  = 'TP.spw'+science_spw,
        datacolumn = 'data',
        width      = 1
        )
    sdimaging(infiles = 'TP.spw'+science_spw,
        outfile = 'TP.spw'+science_spw+'.image',
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

# plot spectrum to check baseline
#################################

for science_spw in science_spws:
    ia.open('TP.spw'+science_spw+'.image')
    spec = ia.getchunk(blc=[0,0,0,0], trc=[63,63,0,2047], inc=1, axes=[0,1], dropdeg=True, getmask=False)
    ia.done()

    fig = plt.figure()
    ax  = plt.subplot(1,1,1)
    ax.plot(spec)
    ax.set_title('band 7, TP, spw '+science_spw)
    ax.set_xlabel('channel')
    ax.set_ylabel('flux')
    fig.savefig('plots/NGC253/002.concat+contsub/rebaseline.band7.TP.spw'+science_spw+'.png', bbox_inches='tight', dpi=300)


####################################################################################################

# flag birdies
##############

# spw 0
# magically, there is no birdy in spw 48
for spw in np.arange(0,184,4):
    if not ( spw == 48 ):
        flagdata(vis = 'TP.spw'+str(spw),
            mode     = 'manual',
            spw      = '0:950~1450',
            action   = 'apply',
            flagbackup = True
            )

# spw 1
for spw in np.arange(1,184,4):
    flagdata(vis = 'TP.spw'+str(spw),
        mode     = 'manual',
        spw      = '0:1810~2047',
        action   = 'apply',
        flagbackup = True
        )


####################################################################################################

# check manually which spw needs re-baselining
##############################################

line_ranges = [['0~600'],
               ['570~950'],
               ['0~670'],
               ['650~900']]

# subtract baseline and image again
for spw in np.arange(0,184):
    lrange = line_ranges[spw%4]

    # invert line range to line-free range
    lfrange = au.invertChannelRanges('0:'+lrange, vis='TP.spw'+str(spw))

    sdbaseline(infile = 'TP.spw'+str(spw),
        outfile    = 'TP.spw'+str(spw)+'.rebaseline',
        datacolumn = 'float_data',
        spw        = lfrange,
        maskmode   = 'list',
        blmode     = 'fit',
        dosubtract = True,
        blformat   = 'text',
        bloutput   = 'TP.spw'+str(spw)+'.bloutput',
        blfunc     = 'poly',
        order      = 1,
        clipthresh = 3.0,
        clipniter  = 0,
        overwrite  = True
        )
    sdimaging(infiles = 'TP.spw'+str(spw)+'.rebaseline',
        outfile = 'TP.spw'+str(spw)+'.rebaseline.image',
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

# plot spectrum to check baseline
#################################

for science_spw in science_spws:
    ia.open('TP.spw'+science_spw+'.rebaseline.image')
    spec = ia.getchunk(blc=[0,0,0,0], trc=[63,63,0,2047], inc=1, axes=[0,1], dropdeg=True, getmask=False)
    ia.done()

    fig = plt.figure()
    ax  = plt.subplot(1,1,1)
    ax.plot(spec)
    ax.set_title('band 7, TP, spw '+science_spw+' REBASELINED')
    ax.set_xlabel('channel')
    ax.set_ylabel('flux')
    fig.savefig('plots/NGC253/002.concat+contsub/rebaseline.band7.TP.spw'+science_spw+'rebaseline.png', bbox_inches='tight', dpi=300)


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
