####################################################################################################


# primary beam correction
#########################

def pbcor(MS_file):

    casalog.post("*"*80)
    casalog.post("FUNCTION: PRIMARY BEAM CORRECTION")
    casalog.post("*"*80)

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)


    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.pbcor'))
    immath(imagename = [os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image'),imbasename+'.deep.pb'],
        mode     = 'evalexpr',
        expr     = 'IM0/IM1',
        outfile  = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.pbcor')
        )


####################################################################################################
