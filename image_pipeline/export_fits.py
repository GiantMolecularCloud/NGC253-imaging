####################################################################################################

# export deep image
###################

def export_fits(MS_file, type='deep'):

    casalog.post("*"*80)
    casalog.post("FUNCTION: EXPORT FITS")
    casalog.post("*"*80)

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)

    for ext in ['image','model','residual','mask','pb']:
        exportfits(imagename  = imbasename+'.'+type+'.'+ext,
                   fitsimage  = imbasename+'.'+type+'.'+ext+'.fits',
                   velocity   = False,
                   optical    = True,
                   overwrite  = True,
                   dropstokes = True,
                   dropdeg    = True,
                   history    = True
                  )

    casalog.post("*"*80)
    casalog.post("FINISHED EXPORTING")
    casalog.post("*"*80)


####################################################################################################
