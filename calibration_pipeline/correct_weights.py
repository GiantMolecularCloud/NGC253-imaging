####################################################################################################

# run statwt for cycle 2 data
#############################


def correct_weights(MS_file, linefree):

    """
    Correct the weights in cycle 2 data. Back then the weights were not meaningful.
    """

    casalog.post("*"*80)
    casalog.post("FUNCTION: CORRECT WEIGHTS")
    casalog.post("*"*80)

    # expand * because statwt cannot deal with all spws
    casalog.post(" * expanding '*' in linefree range")
    linefree_corrected = expand_spw_string(MS_file, linefree)


    casalog.post("*"*80)
    casalog.post("* Getting weights from this range: "+str(linefree))
    casalog.post("* which translates to: "+str(linefree_corrected))
    casalog.post("*"*80)

    # run statwt
    statwt(vis  = MS_file,
        dorms   = False,
        fitspw  = linefree_corrected,
        combine = 'spw',
        minsamp = 2         # default
        )

####################################################################################################
