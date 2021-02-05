####################################################################################################

# manual contsub
################

# load project info
###################

# band 7, ACA, LSB contsub does not work when using a spw:chan list instead of spw:freq but latter
# results in a wrong contsub
# solution: split the MS, run contsub and recombine


####################################################################################################

execfile('NGC253/project_info.py')

casalog.setlogfile(logdir+'NGC253.band7.ACA.ms.LSB.contsub.log')


####################################################################################################

# split MS + contsub
####################

ACA7LSB = datasets[10]

for spw_chan in ACA7LSB['linefree'].split(', '):
    spw  = spw_chan.split(':')[0]
    chan = spw_chan.split(':')[1]

    print("spw: "+spw+"\tchan: "+chan)

    split(vis      = 'NGC253.band7.ACA.ms.LSB',
        outputvis  = 'temp.band7.ACA.LSB.spw'+spw,
        spw        = spw,
        datacolumn = 'data'
        )
    uvcontsub(vis = 'temp.band7.ACA.LSB.spw'+spw,
        fitspw    = '0:'+chan,
        excludechans = False,
        combine   = 'spw',
        fitorder  = 1,
        want_cont = False
        )


####################################################################################################

# concat
########

concat(vis = glob.glob('temp.band7.ACA.LSB.spw*.contsub'),
    concatvis = 'NGC253.band7.ACA.ms.LSB.contsub',
    freqtol   = '',
    copypointing = False
    )


####################################################################################################
