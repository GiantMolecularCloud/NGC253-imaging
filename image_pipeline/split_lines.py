##################
# LINE SPLITTING #
##################

# A script to split out lines from imaged sidebands. Meant to be run seperately from the rest of
# the pipeline.

###################################################################################################

# import required modules
execfile('scripts/casa_imports.py')
execfile('NGC253/project_info.py')


####################################################################################################

lsb_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.LSB.K.image.fits')
usb_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.USB.K.image.fits')

# get line list
lines = parse_line_list('NGC253.lines.band7.txt')
lsb_lines = find_lines(lsb_file, lines)
usb_lines = find_lines(usb_file, lines)

# create mask templates
for im in [lsb_file, usb_file]:
    for w in [200,100,50]:
        mask_cubes(image_file = im,
                   model_file = os.path.join(linedir,'diskfit.total_model.fits'),
                   width      = w*u.km/u.s
                  )



####################################################################################################

# parse line list
#################

def parse_line_list(line_file, vsys=250*u.km/u.s):
    """Parse a line list.

    Parameters
    ----------
    line_file : string
        Txt file containing the lines and their parameters.
    vsys      : astropy velocity
        Systemic velocity. Optional. Needed to convert observed frequency.

    Returns
    -------
    list of dictionaries
        Each dict contains the keys "molecule" (name), "transistion", "restfreq", "obsfreq" (based on
        given vsys), "confidence" (how certain is the detection).
    """

    # load line file
    lines = []
    line_table = np.genfromtxt(line_file,
                 delimiter=(11,)+(25,)+(13,)+(15,)+(14,)+(29,)+(5,),
                 dtype=None
                )

    # clean up und convert
    for row in line_table:
        molecule   = row[0].strip().decode('UTF-8')
        transition = row[1].strip().decode('UTF-8')
        vibration  = row[2].strip().decode('UTF-8')
        restfreq   = float(row[3])*u.GHz
        Eupper     = float(row[4])*u.K
        confidence = row[5].strip().decode('UTF-8')
        seenby     = row[6].strip().decode('UTF-8').replace('\n','')

        if not ( vsys == None ):
            obsfreq = restfreq/(1.+vsys/c.c)                 # optical convention
            lines.append({'molecule': molecule, 'transition': transition, 'vibration': vibration, 'restfreq': restfreq, 'obsfreq': obsfreq, 'Eupper': Eupper, 'confidence': confidence, 'seen_by': seenby})
        else:
            lines.append({'molecule': molecule, 'transition': transition, 'vibration': vibration, 'restfreq': restfreq,                     'Eupper': Eupper, 'confidence': confidence, 'seen_by': seenby})

    return lines


###################################################################################################

# find lines in this image/sideband
###################################

def find_lines(image, lines):
    """Find the lines of a list which are actually contained in an image.

    Parameters
    ----------
    image : string
        File name of the sideband image.
    lines : list
        Line list from parse_line_list.

    Returns
    -------
    list of dictionaries
        Returns a subset of the input line list.
    """

    these_lines = []

    # image info
    header = fits.open(image)[0].header
    naxis3 = int(header['naxis3'])
    crpix3 = int(header['crpix3'])
    crval3 = u.Quantity(str(header['crval3'])+header['cunit3'])
    cdelt3 = u.Quantity(str(header['cdelt3'])+header['cunit3'])

    lower_edge = crval3+(0-crpix3)*cdelt3
    upper_edge = crval3+(naxis3-1.-crpix3)*cdelt3

    # swap upper and lower if frequency step is negative
    if ( lower_edge > upper_edge ):
        le = lower_edge
        ue = upper_edge
        lower_edge = ue
        upper_edge = le

    for line in lines:
        if ( line['obsfreq'] > lower_edge ) and ( line['obsfreq'] < upper_edge ):
            these_lines.append(line)

    return these_lines


###################################################################################################

# create mask cubes
###################

def mask_cubes(image_file, model_file, width, vsys=250*u.km/u.s, chan_width=2.5*u.km/u.s):
    """Create master mask cubes with a certain width around the model velocity.
    The width parameter is meant to be symmetric to the model, i.e. the mask width will be
    twice the specified value at any given pixel.
    """

    # get sideband
    for i in image_file.split('.'):
        if 'SB' in i:
            SB = i
            break
    if SB == 'LSB':
        restfreq = 344.0*u.GHz
    elif SB == 'USB':
        restfreq = 355.8*u.GHz
    else:
        raise Exception("Could not determine sideband.")

    # regrid model to image
    importfits(image_file, 'temp.image')
    imregrid(imagename = model_file,
             output    = 'temp.model',
             template  = 'temp.image',
             asvelocity = False
            )
    exportfits(imagename = 'temp.model',
               fitsimage = os.path.join(linedir, 'diskfit.model.'+SB+'.fits'),
               dropdeg   = True,
               dropstokes = True,
               velocity  = False,
               overwrite = True
              )
    os.system('rm -rf temp.model temp.image')

    # load data
    model = fits.open(os.path.join(linedir, 'diskfit.model.'+SB+'.fits'))[0]
    image = fits.open(image_file)[0]

    # get mask width in pixels
    width_pix = int(np.round((width/chan_width).to(u.dimensionless_unscaled).value))
    print("mask width is +/-"+str(width_pix)+" pixels")

    # convert model to pixel coordinate
    model_pixc = np.round((((model.data*u.km/u.s)-vsys)/chan_width).value).astype(np.int32)+200

    # create empty mask cube
    nx3,nx2,nx1 = image.data.shape
    mask = np.zeros((401,nx2,nx1))

    # # at each model pixel coordinate, set the mask to True within +/- width pixels from the shift
    for (y,x),ch in np.ndenumerate(model_pixc):
        #mask[ch,y,x] = 1.
        mask[ch-width_pix:ch+width_pix+1,y,x] = np.array([1. for i in np.arange(ch-width_pix,ch+width_pix+1)])

    # remove empty channels but keep track which one the central channel was
    cropped_mask = []
    for idx, plane in enumerate(mask):
        if not np.all(plane==0):
            cropped_mask.append(plane)
        if (idx == 200):
            central_chan = len(cropped_mask)
            print("central channel is "+str(central_chan)+" after removing empty channels")
    cropped_mask = np.array(cropped_mask)

    # modify header
    head = copy.copy(image.header)
    del head['history']
    del head['bmaj']
    del head['bmin']
    del head['bpa']
    del head['PC*']
    del head['PV*']
    head['ctype3'] = 'vrad'
    head['cunit3'] = 'km/s'
    head['crval3'] = 0.0
    head['cdelt3'] = chan_width.to(u.km/u.s).value
    head['crpix3'] = central_chan

    # save mask
    fits.writeto(os.path.join(linedir, 'line_mask.'+SB+'.'+str(int(width.value))+'.fits'), data=cropped_mask, header=head, overwrite=True)
    print("wrote "+os.path.join(linedir, 'line_mask.'+SB+'.'+str(int(width.value))+'.fits'))


###################################################################################################

# split out selected lines
##########################

def clean_up_string(string):
    return string.replace('(','').replace(')','').replace(' ','_').replace('*','star').replace('+','plus').replace('=','eq')

def split_lines(image_file, these_lines, vsys=250*u.km/u.s):
    """Split the input image into the given lines. Each image has a given width and is placed in a
    subdirectory of the line directory.

    Parameters
    ----------
    image_file : string
        File name of the sideband image.
    these_lines : list
        Lines to split as given by find_lines.
    vsys : astropy velocity
        Systemic velocity.

    Returns
    -------
    None
        CASA and FITS images of the splitted lines.
    """

    # import fits images
    importfits(image_file, 'temp.image')

    for line in these_lines:

        # open image and get info
        header = fits.getheader(image_file)
        naxis3 = int(header['naxis3'])
        crpix3 = int(header['crpix3'])
        crval3 = u.Quantity(str(header['crval3'])+header['cunit3'])
        cdelt3 = u.Quantity(str(header['cdelt3'])+header['cunit3'])

        # get central channel of the line
        chan_mid = int(np.round(((line['obsfreq']-crval3)/cdelt3).to(u.dimensionless_unscaled).value))

        # split out a subimage centered on this channel
        chan_low  = chan_mid-200 if (chan_mid-200>=0) else 0
        chan_high = chan_mid+200 if (chan_mid+200<=naxis3) else naxis3
        imsubimage(imagename = 'temp.image',
                   outfile   = 'temp.split',
                   chans     = str(chan_low)+'~'+str(chan_high)
                  )

        # get correct mask
        for i in image_file.split('.'):
            if 'SB' in i:
                SB = i
                break
        if ('5' in line['confidence']):
            if (line['molecule'] == 'CO') and (line['vibration'] == 'v=0'):
                width = 200*u.km/u.s
            else:
                width = 100*u.km/u.s
        else:
            width = 50*u.km/u.s


        regrid image to mask (convert to velocity cube)
        imregrid(imagename = 'temp.split',
                 template  = os.path.join(linedir, 'line_mask.'+SB+'.'+str(int(width.value))+'.image'),
                 output    = 'temp.regrid',
                 asvelocity = True
                )
        exportfits(imagename  = 'temp.regrid',
                   fitsimage  = 'temp.regrid.fits',
                   velocity   = True,
                   optical    = True,
                   dropdeg    = True,
                   dropstokes = True,
                   overwrite  = True
                  )

        # apply mask using the fits files
        mask   = fits.open(os.path.join(linedir, 'line_mask.'+SB+'.'+str(int(width.value))+'.fits'))[0]
        regrid = fits.open('temp.regrid.fits')[0]

        # get reference pixels
        ref_regrid =
        ref_mask   = mask.header['crpix3']

        # cut off unnecessary pixels in image
        # apply mask to cube

        immath(imagename = ['temp.regrid', 'temp.mask'],
               mode = 'evalexpr',
               expr = 'IM0*IM1',
               outfile = 'temp.masked'
              )

        # write rest frequency to header
        imhead(imagename = 'temp.masked',
            mode = 'put',
            hdkey = 'restfreq',
            hdvalue = '{:14.12E}'.format((restfreq.to(u.Hz)).value)
            )

        # export to fits
        exportfits(imagename  = 'temp.masked',
                   fitsimage  = os.path.join(linedir, 'NGC253.'+clean_up_string(line['molecule'])+'.'+clean_up_string(line['transition'])+'.'+clean_up_string(line['vibration'])+'.fits'),
                   velocity   = True,
                   optical    = True,
                   dropdeg    = True,
                   dropstokes = True,
                   overwrite  = True
                  )

        # clean up
        os.system('rm -rf temp.split temp.mask temp.regrid temp.split temp.masked')
    os.system('rm -rf temp.image')


        #
        # transition = clean_up_transition(line['transition'])
        # line_file = os.path.join(linedir, line['molecule'], 'NGC253.'+line['molecule']+'_'+transition)
        #
        # # header info
        # header = fits.open(image)[0].header
        # naxis3 = int(header['naxis3'])
        # crpix3 = int(header['crpix3'])
        # crval3 = u.Quantity(str(header['crval3'])+header['cunit3'])
        # cdelt3 = u.Quantity(str(header['cdelt3'])+header['cunit3'])
        #
        # # channels containing the line
        # freq_lo = f_obs(line['restfreq'], vsys-linewidth/2.)
        # freq_hi = f_obs(line['restfreq'], vsys+linewidth/2.)
        # chan_lo = int(round((freq_lo-crval3)/cdelt3))
        # chan_hi = int(round((freq_hi-crval3)/cdelt3))
        #
        # # split out line from large cube
        # os.system('rm -rf '+line_file+'.split.image')
        # imsubimage(imagename = image,
        #     outfile = line_file+'.split.image',
        #     chans   = str(chan_lo)+'~'+str(chan_hi),
        #     mask    = ''
        #     )
        # imhead(imagename = line_file+'.split.image',
        #     mode = 'put',
        #     hdkey = 'restfreq',
        #     hdvalue = str(line['restfreq'])
        #     )
        # exportfits(imagename = line_file+'.split.image',
        #     fitsimage  = line_file+'.split.image.fits',
        #     velocity   = True,
        #     optical    = True,
        #     overwrite  = True,
        #     dropstokes = True,
        #     dropdeg    = True,
        #     history    = False
        #     )
        #
        # # mask only if mask is given
        # if not (line_mask == None ):
        #
        #     # mask everything outside CO velocity range
        #     os.system('rm -rf '+line_file+'.CO_mask.image')
        #     importfits(fitsimage = line_mask,
        #         imagename = line_file+'.CO_mask.image',
        #         overwrite = True,
        #         defaultaxes = True,
        #         defaultaxesvalues = ['','','','I']
        #         )
        #     os.system('rm -rf '+line_file+'.CO_mask.regrid.image')
        #     imregrid(imagename = line_file+'.CO_mask.image',
        #         template = line_file+'.split.image',
        #         output   = line_file+'.CO_mask.regrid.image',
        #         asvelocity = True
        #         )
        #     os.system('rm -rf '+line_file+'.line_mask')
        #     immath(imagename  = line_file+'.CO_mask.regrid.image',
        #         mode    = 'evalexpr',
        #         expr    = 'iif(IM0>0,1,0)',
        #         outfile = line_file+'.line_mask',
        #         mask    = '"NGC253.CO_3-2.mom0_150.mask"',
        #         stretch = True
        #         )
        #     os.system('rm -rf '+line_file+'.mask.image')
        #     immath(imagename  = [line_file+'.split.image',line_file+'.line_mask'],
        #         mode    = 'evalexpr',
        #         expr    = 'IM0*IM1',
        #         outfile = line_file+'.mask.image'
        #         )
        #     exportfits(imagename = line_file+'.mask.image',
        #         fitsimage  = line_file+'.mask.image.fits',
        #         velocity   = True,
        #         optical    = True,
        #         overwrite  = True,
        #         dropstokes = True,
        #         dropdeg    = True,
        #         history    = False
        #         )


###################################################################################################
