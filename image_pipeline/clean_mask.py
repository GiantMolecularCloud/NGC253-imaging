####################################################################################################

# create dirty mask
###################

def clean_mask(MS_file, mask_thresh=75, include_failing_regions = True):

    casalog.post("*"*80)
    casalog.post("FUNCTION: MAKE MASK")
    casalog.post("*"*80)

    imagedir, subdir, source, band, array, sideband = get_path_info(MS_file)
    MS_idx, imsize, cell, noise, major, minor, pa = get_image_info(MS_file)

    imbasename = os.path.join(imagedir,subdir,source+'.'+band+'.'+array+'.'+sideband)

    badchans = image_setups[get_idx(image_setups, MS_file, key='MS')]['bad chans']

    os.system('mkdir -p '+os.path.join(imagedir,subdir,'masks'))

    # assemble joint mask of the failing regions and regrid
    if include_failing_regions:
        failing_region_masks = sorted(glob.glob(os.path.join(imagedir,'masks','failing_region_?.mask')))
        exp = 'abs('
        for idx,i in enumerate(failing_region_masks):
            if ( idx == 0 ):
                exp+='(IM'+str(idx)+'-1)'
            else:
                exp+='*(IM'+str(idx)+'-1)'
        exp += ')'
        os.system('rm -rf '+os.path.join(imagedir,subdir,'masks','failing_region_sum.mask'))
        immath(imagename = failing_region_masks,
            mode     = 'evalexpr',
            expr     = exp,
            outfile  = os.path.join(imagedir,subdir,'masks','failing_region_sum.mask')
            )

    # generate maximum outline mask and regrid
    os.system('rm -rf '+os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thresh)+'.mask'))
    immath(imagename = os.path.join(imagedir,'masks','NGC253.band7.12m-mid.CO_3-2.mom0.arm_removed.image'),
        mode     = 'evalexpr',
        expr     = 'iif(IM0>'+str(mask_thresh)+',1,0)',
        outfile  = os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thresh)+'.mask')
        )

    # merge masks
    if include_failing_regions:
        os.system('rm -rf '+os.path.join(imagedir,subdir,'masks','combined.mask'))
        immath(imagename = [os.path.join(imagedir,subdir,'masks','failing_region_sum.mask'),os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thresh)+'.mask')],
            mode     = 'evalexpr',
            expr     = 'IM0*IM1',
            outfile  = os.path.join(imagedir,subdir,'masks','combined.mask')
            )
    else:
        os.system('ln -s '+os.path.join(imagedir,subdir,'masks','mom0_'+str(mask_thresh)+'.mask')+' '+os.path.join(imagedir,subdir,'masks','combined.mask'))


    casalog.post("*"*80)
    casalog.post("FINISHED MASKING")
    casalog.post("*"*80)
