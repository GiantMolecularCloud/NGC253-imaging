####################################################################################################

# split out sidebands
#####################


def split_sidebands(MS_file, datacolumn='data'):

    """
    Split an MS into upper and lower sideband.
    This task appends .LSB or .USB to the file name.
    """

    casalog.post("*"*80)
    casalog.post("FUNCTION: SPLIT SIDEBANDS")
    casalog.post("*"*80)

    # get the spectral window information
    ms.open(MS_file)
    spw_info = ms.getspectralwindowinfo()
    ms.close()

    # select lower and upper sidebands
    lsb_spws = []
    usb_spws = []
    distinctionFreq = np.mean([spw_info[spw]['Chan1Freq'] for spw in spw_info.keys()])
    for spw in spw_info.keys():
        if (spw_info[spw]['Chan1Freq'] < distinctionFreq):
            lsb_spws.append(spw)
        elif (spw_info[spw]['Chan1Freq'] > distinctionFreq):
            usb_spws.append(spw)
        else:
            raise ValueError("Something went wrong with deciding if spw "+str(spw)+"is in the lower or upper sideband.")
    # sort spws and reformat so casa understands
    lsb_spws = ','.join(sorted(lsb_spws))
    usb_spws = ','.join(sorted(usb_spws))

    # split out lower sideband
    casalog.post("*"*80)
    casalog.post("* Splitting out lower sideband containing spw "+str(lsb_spws))
    casalog.post("*"*80)
    split(vis      = MS_file,
        outputvis  = MS_file+'.LSB',
        spw        = lsb_spws,
        datacolumn = datacolumn,
        width      = 1
        )
    casalog.post("*"*80)
    casalog.post("* Generating listobs for "+MS_file+".LSB")
    casalog.post("*"*80)
    listobs(vis    = MS_file+'.LSB',
        selectdata = False,
        listfile   = MS_file+'.LSB.listobs'
        )

    # split out upper sideband
    casalog.post("*"*80)
    casalog.post("* Splitting out upper sideband containing spw "+str(lsb_spws))
    casalog.post("*"*80)
    split(vis      = MS_file,
        outputvis  = MS_file+'.USB',
        spw        = usb_spws,
        datacolumn = datacolumn,
        width      = 1
        )
    casalog.post("*"*80)
    casalog.post("* Generating listobs for "+MS_file+".USB")
    casalog.post("*"*80)
    listobs(vis    = MS_file+'.USB',
        selectdata = False,
        listfile   = MS_file+'.USB.listobs'
        )


####################################################################################################
