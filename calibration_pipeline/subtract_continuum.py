####################################################################################################

# run continuum subtraction
###########################


def subtract_continuum(MS_file, linefree, fitorder=1):

    """
    Fit and subtract the continuum.
    The line-free range needs to be given as the second argument. Fitorder defaults to 0.
    """

    casalog.post("*"*80)
    casalog.post("FUNCTION: SUBTRACT CONTINUUM")
    casalog.post("*"*80)

    # subtract continuum
    casalog.post("*"*80)
    casalog.post("* Fitting continuum to this range: "+str(linefree))
    casalog.post("*"*80)

    # fit and subtract continuum
    uvcontsub(vis    = MS_file,
        field        = '',
        fitspw       = linefree,
        excludechans = False,
        combine      = 'spw',
        fitorder     = fitorder
        )

####################################################################################################
