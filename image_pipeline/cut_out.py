####################################################################################################

# cut out image
###############

def cut_out_images(MS_file):

    casalog.post("*"*80)
    casalog.post("FUNCTION: CUT OUT IMAGES")
    casalog.post("*"*80)

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)

    cutbox   = image_setups[get_idx(image_setups, MS_file, key='MS')]['cutbox']

    imsubimage(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.pbcor'),
               outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.pbcor.sub'),
               box       = cutbox,
               chans     = '',
               dropdeg   = True,
               overwrite = True
              )
    imsubimage(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image'),
               outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.K.image.sub'),
               box       = cutbox,
               chans     = '',
               dropdeg   = True,
               overwrite = True
              )
    imsubimage(imagename = imbasename+'.deep.mask',
               outfile   = imbasename+'.deep.mask.sub',
               box       = cutbox,
               chans     = '',
               dropdeg   = True,
               overwrite = True
              )


####################################################################################################
