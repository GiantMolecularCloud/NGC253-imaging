####################################################################################################

# convert to K
##############

# immath produces an unuseable image (cannot be exported, nor proced by any other task)
# use astropy instead

def convert_K(MS_file):

    casalog.post("*"*80)
    casalog.post("FUNCTION: CONVERT TO BRIGHTNESS TEMPERATURE")
    casalog.post("*"*80)

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)


    im = fits.open(os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.image.fits'))[0]
    restfreq = (im.header['restfrq']*u.Hz).to(u.GHz)
    bmin     = (im.header['bmin']*u.degree).to(u.arcsec)
    bmaj     = (im.header['bmaj']*u.degree).to(u.arcsec)
    factor   = float( 1.226e6/(restfreq.value**2*bmin.value*bmaj.value) )
    im.data *= factor
    im.header['bunit'] = 'K'
    fits.writeto(os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.fits'), data=im.data, header=im.header, overwrite=True)

    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image'))
    importfits(fitsimage = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.fits'),
               imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image')
              )


####################################################################################################
