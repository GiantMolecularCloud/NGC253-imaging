####################################################################################################

# feather TP and array
######################


def feather_TP(MS_file, sdfactor=1.0):

    casalog.post("*"*80)
    casalog.post("FUNCTION: FEATHER TOTAL POWER")
    casalog.post("*"*80)

    casalog.setlogfile(os.path.join(logdir,MS_file+'.imaging.log'))

    # collect information about the image
    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)
    chanwidth, restfreq = set_frequency(band)
    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)


    # regrid TP image to array image
    specsmooth(imagename = os.path.join(imagedir,source+'.'+band+'.TP.'+sideband+'.image'),
               outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.smooth.image'),
               function  = 'hanning',
               dmethod   = 'copy',
               axis      = -1,
               overwrite = True
              )
    imregrid(imagename  = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.smooth.image'),
             template   = imbasename+'.deep.image',
             output     = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.regrid.image'),
             asvelocity = False,
             overwrite  = True
            )
    tempim = 'temp_'+str(int(np.random.rand()*1e4))+'.image'
    ia.open(os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.regrid.image'))
    ia.adddegaxes(stokes  = 'I',
                  outfile = os.path.join(imagedir,subdir,tempim)
                 )
    ia.unlock()
    ia.close()
    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.stokes.image'))
    imtrans(imagename = os.path.join(imagedir,subdir,tempim),
          outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.stokes.image'),
          order     = ['right','dec','stokes','freq']
         )
    os.system('rm -rf '+os.path.join(imagedir,subdir,tempim))

    # multiply TP image by array response function
    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.pb_multiplied.image'))
    immath(imagename = [os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.stokes.image'),imbasename+'.deep.pb'],
        mode     = 'evalexpr',
        expr     = 'IM0*IM1',
        outfile  = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.pb_multiplied.image')
        )


    # feather
    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image'))
    feather(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.image'),
        highres  = imbasename+'.deep.image',
        lowres   = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.pb_multiplied.image'),
        sdfactor = sdfactor
        )
    exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.image'),
        fitsimage  = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.'+sideband+'.image.fits'),
        velocity   = False,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )


####################################################################################################
