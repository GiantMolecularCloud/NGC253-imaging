####################################################################################################

# export final images
#####################

def export_final(MS_file):

    casalog.post("*"*80)
    casalog.post("FUNCTION: EXPORT FINAL IMAGES")
    casalog.post("*"*80)

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)


    exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.pbcor.sub'),
        fitsimage  = os.path.join(finaldir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.pbcor.fits'),
        velocity   = False,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )
    exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.sub'),
        fitsimage  = os.path.join(finaldir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.fits'),
        velocity   = False,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )
    exportfits(imagename = imbasename+'.deep.mask.sub',
        fitsimage  = os.path.join(finaldir,source+'.'+band+'.TP+'+array+'.'+sideband+'.mask.fits'),
        velocity   = False,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )


####################################################################################################
