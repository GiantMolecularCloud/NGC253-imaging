####################################################################################################
# image NGC 253 # band 7 # ACA+12m-mid+12m-high # CO (3-2) #
####################################################################################################

execfile('scripts/casa_imports.py')
execfile('scripts/NGC253/image_pipeline/import_pipeline.py')
execfile('NGC253/project_info.py')


####################################################################################################

steps    = ['feather', 'convert K', 'pbcor', 'subimage', 'moments', 'export images']

MS_file  = 'NGC253.band7.ACA+12m-mid+12m-high.ms.LSB.contsub.regrid'
mask_thres = 75
box   = '126,148,1227,1117'
chans = '6~249'

imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
subdir = source+'.'+band+'.'+array+'.CO_3-2'
imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.CO_3-2')


####################################################################################################

# dirty image
#############

if 'dirty image' in steps:
    os.system('mkdir -p '+os.path.join(imagedir, subdir))
    tclean(vis            = os.path.join(imagedir,'visdir',MS_file),
           selectdata     = False,
           datacolumn     = 'data',
           imagename      = imbasename+'.dirty',
           imsize         = 1280,
           cell           = '0.05arcsec',
           phasecenter    = phasecenter,
           specmode       = 'cube',
           nchan          = 250,
           start          = '0.0km/s',
           width          = '2.5km/s',
           outframe       = 'LSRK',
           veltype        = 'optical',
           restfreq       = '345.79598990GHz',
           interpolation  = 'linear',
           gridder        = 'mosaic',
           chanchunks     = 1,
           mosweight      = True,
           pblimit        = 0.1,
           deconvolver    = 'multiscale',
           scales         = [0,3,9,27,81],
           smallscalebias = 0.6,
           restoration    = True,
           restoringbeam  = ['0.17arcsec','0.13arcsec','-75.1deg'],
           pbcor          = False,
           weighting      = 'briggs',
           robust         = 0.5,
           niter          = 0,
           gain           = 0.1,
           threshold      = '1.8mJy',
           usemask        = 'user',
           mask           = '',
           restart        = True,
           calcres        = True,
           calcpsf        = True
           )

####################################################################################################

# mask
######

if 'clean mask' in steps:

    os.system('mkdir -p '+os.path.join(imagedir,subdir,'masks'))

    # assemble joint mask of the failing regions and regrid
    failing_region_masks = sorted(glob.glob(os.path.join(imagedir,'masks','failing_region_?.mask')))
    exp = 'abs('
    for idx,i in enumerate(failing_region_masks):
        if ( idx == 0 ):
            exp+='(IM'+str(idx)+'-1)'
        else:
            exp+='*(IM'+str(idx)+'-1)'
    exp += ')'
    os.system('rm -rf '+os.path.join(imagedir,'masks','failing_region_sum.mask'))
    immath(imagename = failing_region_masks,
        mode     = 'evalexpr',
        expr     = exp,
        outfile  = os.path.join(imagedir,subdir,'masks','failing_region_sum.mask')
        )
    imregrid(imagename  = os.path.join(imagedir,subdir,'masks','failing_region_sum.mask'),
             template   = imbasename+'.dirty.image',
             output     = os.path.join(imagedir,subdir,'masks','failing_region_sum.regrid.mask'),
             asvelocity = False,
             overwrite  = True
            )
    # generate maximum outline mask and regrid
    os.system('rm -rf '+os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thres)+'.mask'))
    immath(imagename = os.path.join(imagedir,'masks','NGC253.band7.12m-mid.CO_3-2.mom0.arm_removed.image'),
        mode     = 'evalexpr',
        expr     = 'iif(IM0>'+str(mask_thres)+',1,0)',
        outfile  = os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thres)+'.mask')
        )
    imregrid(imagename  = os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thres)+'.mask'),
             template   = imbasename+'.dirty.image',
             output     = os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thres)+'.regrid.mask'),
             asvelocity = False,
             overwrite  = True
            )
    # merge masks
    os.system('rm -rf '+os.path.join(imagedir,subdir,'masks','combined.mask'))
    immath(imagename = [os.path.join(imagedir,subdir,'masks','failing_region_sum.regrid.mask'),os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thres)+'.regrid.mask')],
        mode     = 'evalexpr',
        expr     = 'IM0*IM1',
        outfile  = os.path.join(imagedir,subdir,'masks','combined.mask')
        )


####################################################################################################

# deep image
############

if 'deep image' in steps:
    for f in glob.glob(imbasename+'.dirty'):
        os.system('cp -r '+f+' '+f.replace('dirty','deep'))
    os.system('rm -rf '+imbasename+'.dirty.mask')

    tclean(vis            = os.path.join(imagedir,'visdir',MS_file),
           selectdata     = False,
           datacolumn     = 'data',
           imagename      = imbasename+'.deep',
           imsize         = 1280,
           cell           = '0.05arcsec',
           phasecenter    = phasecenter,
           specmode       = 'cube',
           nchan          = 250,
           start          = '0.0km/s',
           width          = '2.5km/s',
           outframe       = 'LSRK',
           veltype        = 'optical',
           restfreq       = '345.79598990GHz',
           interpolation  = 'linear',
           gridder        = 'mosaic',
           chanchunks     = 1,
           mosweight      = True,
           pblimit        = 0.1,
           deconvolver    = 'multiscale',
           scales         = [0,3,9,27,81],
           smallscalebias = 0.6,
           restoration    = True,
           restoringbeam  = ['0.17arcsec','0.13arcsec','-75.1deg'],
           pbcor          = False,
           weighting      = 'briggs',
           robust         = 0.5,
           niter          = 250000000,
           gain           = 0.1,
           threshold      = '1.8mJy',
           usemask        = 'user',
           mask           = os.path.join(imagedir,subdir,'masks','combined.mask'),
           restart        = True,
           calcres        = True,
           calcpsf        = True
           )


####################################################################################################

# export fits images
####################

if 'export deep' in steps:
    for ext in ['image','model','residual','mask','pb']:
        exportfits(imagename  = imbasename+'.deep.'+ext,
                   fitsimage  = imbasename+'.deep.'+ext+'.fits',
                   velocity   = False,
                   optical    = True,
                   overwrite  = True,
                   dropstokes = True,
                   dropdeg    = True,
                   history    = True
                  )


####################################################################################################

# feather totel power
#####################

if 'feather' in steps:

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
    feather(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image'),
        highres  = imbasename+'.deep.image',
        lowres   = os.path.join(imagedir,subdir,source+'.'+band+'.TP.'+sideband+'.pb_multiplied.image'),
        sdfactor = 1.0
        )
    exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image'),
        fitsimage  = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.fits'),
        velocity   = False,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )


####################################################################################################

# convert to K
##############

# immath produces an unuseable image (cannot be exported, nor proced by any other task)
# use astropy instead

if 'convert K' in steps:

    im = fits.open(os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.fits'))[0]
    restfreq = (im.header['restfrq']*u.Hz).to(u.GHz)
    bmin     = (im.header['bmin']*u.degree).to(u.arcsec)
    bmaj     = (im.header['bmaj']*u.degree).to(u.arcsec)
    factor   = float( 1.226e6/(restfreq.value**2*bmin.value*bmaj.value) )
    im.data *= factor
    im.header['bunit'] = 'K'
    fits.writeto(os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image.fits'), data=im.data, header=im.header, overwrite=True)

    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image'))
    importfits(fitsimage = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image.fits'),
               imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image')
              )


####################################################################################################


# primary beam correction
#########################

if 'pbcor' in steps:
    os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.pbcor'))
    immath(imagename = [os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image'),imbasename+'.deep.pb'],
        mode     = 'evalexpr',
        expr     = 'IM0/IM1',
        outfile  = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.pbcor')
        )


####################################################################################################

# cut out image
###############

if 'subimage' in steps:

    imsubimage(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image'),
               outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image.sub'),
               box       = box,
               chans     = chans,
               dropdeg   = True,
               overwrite = True
              )
    imsubimage(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.pbcor'),
               outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.pbcor.sub'),
               box       = box,
               chans     = chans,
               dropdeg   = True,
               overwrite = True
              )
    imsubimage(imagename = imbasename+'.deep.mask',
               outfile   = imbasename+'.deep.mask.sub',
               box       = box,
               chans     = chans,
               dropdeg   = True,
               overwrite = True
              )


####################################################################################################

# moment maps
#############

if 'moments' in steps:
    for mom in [0,1,2]:
        os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_3sigma.image'))
        immoments(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image.sub'),
                  outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_3sigma.image'),
                  moments   = [mom],
                  chans     = '',
                  mask      = '',
                  includepix = [0.00216,1000]
                  )
        os.system('rm -rf '+os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_cmask_3sigma.image'))
        immoments(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image.sub'),
                  outfile   = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_cmask_3sigma.image'),
                  moments   = [mom],
                  chans     = '',
                  mask      = '"'+imbasename+'.deep.mask.sub"',
                  includepix = [0.00216,1000]
                  )



####################################################################################################

# export final images
#####################

if 'export images' in steps:

    exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.K.image.sub'),
        fitsimage  = os.path.join(imagedir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.fits'),
        velocity   = True,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )
    exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.pbcor.sub'),
        fitsimage  = os.path.join(imagedir,source+'.'+band+'.TP+'+array+'.CO_3-2.image.pbcor.fits'),
        velocity   = True,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )
    exportfits(imagename = imbasename+'.deep.mask.sub',
        fitsimage  = os.path.join(imagedir,source+'.'+band+'.TP+'+array+'.CO_3-2.mask.fits'),
        velocity   = True,
        optical    = True,
        overwrite  = True,
        dropstokes = True,
        dropdeg    = True,
        history    = True
        )
    for mom in [0,1,2]:
        exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_3sigma.image'),
            fitsimage  = os.path.join(imagedir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_3sigma.fits'),
            velocity   = True,
            optical    = True,
            overwrite  = True,
            dropstokes = True,
            dropdeg    = True,
            history    = True
            )
        exportfits(imagename = os.path.join(imagedir,subdir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_cmask_3sigma.image'),
            fitsimage  = os.path.join(imagedir,source+'.'+band+'.TP+'+array+'.CO_3-2.mom'+str(mom)+'_cmask_3sigma.fits'),
            velocity   = True,
            optical    = True,
            overwrite  = True,
            dropstokes = True,
            dropdeg    = True,
            history    = True
            )


####################################################################################################
