##################
# LINE SPLITTING #
##################

# A script to split out lines from imaged sidebands. Meant to be run seperately from the rest of
# the pipeline.

###################################################################################################

# import required modules
#execfile('scripts/python_imports.py')    # superceded by python_startup
execfile('NGC253/project_info.py')


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
###################################################################################################

def mask_cube_velocity(image_file, model_file, modeldir, width, vsys, chan_width):
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

    os.system('mkdir -p '+os.path.join(linedir, modeldir))

    # regrid model to image using CASA
    # this can be done easily in CASA but is difficult in python.
    run_in_casa(f"""
execfile('scripts/casa_imports.py')
execfile('NGC253/810.ISM_relations/info.py')
importfits('{image_file}', 'temp.image')
imregrid(imagename = '{model_file}',
         output    = 'temp.model',
         template  = 'temp.image',
         asvelocity = False
        )
exportfits(imagename = 'temp.model',
           fitsimage = os.path.join('{linedir}', '{modeldir}', 'model_mask.'+'{SB}'+'.fits'),
           dropdeg   = True,
           dropstokes = True,
           velocity  = False,
           overwrite = True
          )
os.system('rm -rf temp.model temp.image')
    """)

    # load data
    model = fits.open(os.path.join(linedir, modeldir, 'model_mask.'+SB+'.fits'))[0]
    image = fits.open(image_file)[0]

    # get mask width in pixels
    width_pix  = int(np.round((width/chan_width).to(u.dimensionless_unscaled).value))
    print("mask width is +/-"+str(width_pix)+" pixels")

    # convert model to pixel coordinate
    #model_pixc = np.round((((model.data*u.km/u.s)-vsys)/chan_width).value).astype(np.int32)+200        # causes problems with nan
    model_pixc = np.round((((model.data*u.km/u.s)-vsys)/chan_width).value)+200

    # create empty mask cube
    nx3,nx2,nx1 = image.data.shape
    mask = np.zeros((401,nx2,nx1))

    # # at each model pixel coordinate, set the mask to True within +/- width pixels from the shift
    for (y,x),ch in np.ndenumerate(model_pixc):
        if not np.isnan(ch):
            ch = int(ch)
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
    head['ctype3'] = 'VOPT'
    head['cunit3'] = 'km/s'
    head['crval3'] = 0.0
    head['cdelt3'] = chan_width.to(u.km/u.s).value
    head['crpix3'] = central_chan

    # save mask
    fits.writeto(os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(int(width.value))+'.fits'), data=cropped_mask, header=head, overwrite=True)
    print("wrote "+os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(int(width.value))+'.fits'))


def mask_cube_threshold(image_file, model_file, modeldir, threshold, vsys, chan_width):
    """
    Create master mask cubes from a cube and an intensity threshold. All values above the threshold
    will be considered in the mask, everything below is masked out.
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

    os.system('mkdir -p '+os.path.join(linedir, modeldir))

    # load data
    image = fits.open(image_file)[0]
    model = fits.open(model_file)[0]

    # create empty mask cube
    nx3,nx2,nx1 = image.data.shape
    mask = np.zeros((401,nx2,nx1))

    # modify header
    head = copy.copy(image.header)
    del head['history']
    del head['bmaj']
    del head['bmin']
    del head['bpa']
    del head['PC*']
    del head['PV*']
    head['ctype3'] = 'VOPT'
    head['cunit3'] = 'km/s'
    head['crval3'] = 250.0
    head['cdelt3'] = chan_width.to(u.km/u.s).value
    head['crpix3'] = 201
    head['restfrq'] = model.header['restfrq']

    # write temporary mask to file for regridding
    fits.writeto('temp.mask.fits', data=mask, header=head)

    # regrid model to temporary mask using CASA
    # this can be done easily in CASA but is difficult in python.
    run_in_casa(f"""
execfile('scripts/casa_imports.py')
execfile('NGC253/810.ISM_relations/info.py')
importfits('{model_file}', 'temp.model.image')
importfits('temp.mask.fits', 'temp.mask.image')
imregrid(imagename = 'temp.model.image',
         output    = 'temp.model.regrid.image',
         template  = 'temp.mask.image',
         asvelocity = False
        )
exportfits(imagename = 'temp.model.regrid.image',
           fitsimage = os.path.join('{linedir}', '{modeldir}', 'model_mask.'+'{SB}'+'.fits'),
           dropdeg   = True,
           dropstokes = True,
           velocity  = False,
           overwrite = True
          )
os.system('rm -rf temp.mask.fits temp.model.image temp.mask.image temp.model.regrid.image')
    """)

    # load regridded model
    mask = fits.open(os.path.join(linedir, modeldir, 'model_mask.'+SB+'.fits'))[0]

    # set mask to true where image is above threshold
    threshold = threshold.to(u.Quantity('1.0'+mask.header['bunit'])).value
    mask.data[mask.data < threshold] = 0
    mask.data[mask.data >= threshold] = 1
    mask.data[np.isnan(mask.data)] = 0

    # remove empty channels
    cropped_mask = []
    for idx, plane in enumerate(mask.data):
        if not np.all(plane==0):
            cropped_mask.append(plane)
        if (idx == 200):
            central_chan = len(cropped_mask)
            print("central channel is "+str(central_chan)+" after removing empty channels")
    cropped_mask = np.array(cropped_mask)

    # remove header info that was added by CASA
    del mask.header['bmaj']
    del mask.header['bmin']

    # adjust header to match the other masks
    mask.header['ctype3'] = 'VOPT'
    mask.header['cunit3'] = 'km/s'
    mask.header['crval3'] = 250.0
    mask.header['cdelt3'] = chan_width.to(u.km/u.s).value
    mask.header['crpix3'] = central_chan

    # save mask
    fits.writeto(os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(threshold)+'.fits'), data=cropped_mask, header=mask.header, overwrite=True)
    print("wrote "+os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(threshold)+'.fits'))


def mask_cube(image_file, model_file, modeldir, width=100*u.km/u.s, threshold=5*u.K, vsys=250*u.km/u.s, chan_width=2.5*u.km/u.s):
    """
    Create master mask cubes from a given model. This can be either a velocity and a velocity
    range or a cube and a threshold.
    """

    model = fits.open(model_file)[0]
    naxis = model.header['naxis']

    if (naxis == 2):
        mask_cube_velocity(image_file, model_file, modeldir, width, vsys, chan_width)
    if (naxis == 3):
        mask_cube_threshold(image_file, model_file, modeldir, threshold, vsys, chan_width)


###################################################################################################
# split out selected lines
###################################################################################################

def clean_up_string(string):
    return string.replace('(','').replace(')','').replace(' ','_')

def get_line_file_name(line, image_file=''):
    linefilename = 'NGC253.'+clean_up_string(line['molecule'])+'_'+clean_up_string(line['transition'])
    if not ( line['vibration'] == '' ):
        linefilename += '_'+clean_up_string(line['vibration'])
    if 'pbcor' in image_file:
        linefilename += '.pbcor'
    linefilename += '.fits'
    return linefilename

def split_line(image_file, line, modeldir, overwrite=True):
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

    # get sideband
    for i in image_file.split('.'):
        if 'SB' in i:
            SB = i
            break

    # load image and get info
    image = SpectralCube.read(image_file)
    naxis3 = int(image.header['naxis3'])
    crpix3 = int(image.header['crpix3'])
    crval3 = u.Quantity(str(image.header['crval3'])+image.header['cunit3'])
    cdelt3 = u.Quantity(str(image.header['cdelt3'])+image.header['cunit3'])

    # get central channel of the line
    chan_mid = int(np.round(((line['obsfreq']-crval3)/cdelt3).to(u.dimensionless_unscaled).value))

    # split out a subimage centered on chan_mid
    # if the range would extend beyong the image, crop the range to fit the image
    # keep track which pixel of the new cube corresponds to systemic velocity
    if (chan_mid-150 >= 0) & (chan_mid+150 <= naxis3):
        chan_low  = chan_mid-150
        chan_high = chan_mid+150
        chan_ref  = 150
    elif (chan_mid-150 < 0) & (chan_mid+150 <= naxis3):
        chan_low  = 0
        chan_high = chan_mid+150
        chan_ref  = chan_mid
    elif (chan_mid-150 >= 0) & (chan_mid+150 > naxis3):
        chan_low  = chan_mid-150
        chan_high = naxis3-1
        chan_ref  = 150
    split = image[chan_low:chan_high,:,:]

    # get correct mask
    if (modeldir == 'diskfit') or (modeldir == 'CO_velocity'):
        if ('5' in line['confidence']):
            if (line['molecule'] == 'CO') and (line['vibration'] == 'v=0'):
                width = 200*u.km/u.s
            else:
                width = 150*u.km/u.s
        elif ('4' in line['confidence']) or ('3' in line['confidence']):
            width = 100*u.km/u.s
        else:
            width = 100*u.km/u.s
        mask = SpectralCube.read(os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(int(width.value))+'.fits'))
    elif (modeldir == 'CO_threshold'):
        if ('5' in line['confidence']) or ('4' in line['confidence']) or ('3' in line['confidence']):
            threshold = 1.0
            mask = SpectralCube.read(os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(threshold)+'.fits'))
        else:
            threshold = 3.5
            mask = SpectralCube.read(os.path.join(linedir, modeldir, 'line_mask.'+SB+'.'+str(threshold)+'.fits'))
    else:
        raise Exception("Unknown model directory / model type.")

    # regrid split cube to be equidistant in velocity
    # this requires flipping the reference pixel that points to the channel at vsys
    # the large new velocity axis assured that the cube is always bigger than the mask which makes aligning easier
    print("\nRegridding "+line['molecule']+" "+line['transition']+" to equidistant velocity channels for model "+modeldir+".")
    split_velo = split.with_spectral_unit(u.km/u.s, velocity_convention='optical', rest_value=line['restfreq'])
    velo_axis  = np.arange(-100,601,2.5)*u.km/u.s
    velo_cube  = split_velo.spectral_interpolate(velo_axis, fill_value=0.)

    # get reference pixels in cube and mask
    # reference pixel marks velocity==250, nchan is length of the cube
    # note that the reference pixel depends on the velocity axis that the cube was regridded to. For 281 channels from -100 to 600, vsys is at channel 140
    mref    = int(mask.header['crpix3'])
    mnchan  = int(mask.header['naxis3'])
    cref    = 140
    cnchan  = int(velo_cube.header['naxis3'])

    # align mask and cube by taking only the mutual overlap
    # three cases: mask within cube, mask surpassing cube to either side
    if (cref >= mref) & (cnchan-cref >= mnchan-mref):
        submask = mask
        subcube = velo_cube[cref-mref:cref-mref+mnchan,:,:]
    elif (cref < mref) & (cnchan-cref > mnchan-mref):
        submask = mask[mref-cref:,:,:]
        subcube = velo_cube[:,mnchan+cref-mref,:,:]
    elif (cref >= mref) & (cnchan-cref < mnchan-mref):
        submask = mask[:cnchan+mref-cref,:,:]
        subcube = velo_cube[cref-mref:,:,:]
    else:
        raise Exception("Could not determine relative overlap between mask and cube.")

    # apply mask to cube
    line_cube = subcube.with_mask(submask.unmasked_data[:,:,:].value>0.5)

    # write correct restfrequency
    line_cube.header['restfrq'] = line['restfreq'].to(u.Hz).value

    # export to fits
    linefilename = get_line_file_name(line, image_file)
    line_cube.write(os.path.join(linedir, modeldir, linefilename), overwrite=overwrite)


###################################################################################################
# image lines
###################################################################################################

def format_tex(line):
    m = line['molecule']
    t = line['transition'].replace('-','--').replace('_',r'\_')
    v = line['vibration'].replace('_',r'\_')
    if (v == ''):
        return m+' ('+t+')'
    else:
        return m+' ('+t+' '+v+')'

def plot_moment(line, modeldir):
    """
    Plot moment maps of all lines to get an overview.
    """

    # file names
    line_file = os.path.join(linedir, modeldir, get_line_file_name(line))
    mom0_file = line_file.replace('fits','mom0.fits')

    if os.path.exists(line_file):
        print('Generating moment: '+line_file)

        # generate moment
        if not os.path.exists(mom0_file):
            cube = SpectralCube.read(line_file)
            mom0 = cube.moment(order=0).to(u.K*u.km/u.s)
            mom0.write(mom0_file, overwrite=True)

        # plot moment
        vmin = np.nanmin(fits.getdata(mom0_file))
        vmax = np.nanmax(fits.getdata(mom0_file))
        cmax = np.round(vmax,-1*int(np.floor(np.log10(vmax))))
        cran = [cmax/64., cmax/16., cmax/4., cmax]

        easy_aplpy.plot.map(mom0_file,
            figsize   = (16,16),
            cmap      = easy_aplpy.custom_colormaps.viridis_cropped,
            stretch   = 'sqrt',
            vmin      = vmin,
            vmax      = vmax,
            recenter  = [SkyCoord('00h47m33.01s -25d17m17.0s'), 46.0*u.arcsec, 36.0*u.arcsec],
            contours  = [[mom0_file, cran, 'black']],
            colorbar  = ['right', 'F [K\,km\,s$^{-1}$]'],
            scalebar  = [14.73*u.arcsec, '250\,pc', 'bottom left'],
            beam      = None, #'bottom right',
            texts     = [[[0.5,1.0], format_tex(line), {'size':32, 'ha':'center', 'va':'center', 'style':'oblique', 'weight':'black', 'color':'black', 'bbox': {'boxstyle': 'round', 'facecolor': 'w', 'edgecolor': 'black', 'linewidth': 0.5}}]],
            out       = os.path.join(mom0_file.replace('fits','pdf'))
            )
    else:
        print('Does not exist: '+line_file)

def plot_spectrum(line, modeldir, where=SkyCoord('11.887444 deg','-25.288816 deg')):
    """
    Plot a spectrum on the continuum peak. Shows if the mask is narrow enough or if other lines
    are in the image as well.
    """

    line_file = os.path.join(linedir, modeldir, get_line_file_name(line))

    if os.path.exists(line_file):
        print('Plotting spectrum: '+line_file)

        cube = SpectralCube.read(line_file)

        # coordinates to pixel location
        x,y = [int(np.round(i)) for i in WCS(cube.header).all_world2pix(where.ra, where.dec, 0, 1)[0:2]]

        fig = plt.figure(figsize=(16,8))
        ax  = plt.subplot(1,1,1)
        ax.text(0.5, 1.0, format_tex(line), size=32, ha='center', va='center', transform = ax.transAxes, color='black', bbox={'boxstyle': 'round', 'facecolor': 'w', 'edgecolor': 'black', 'linewidth': 0.5})
        ax.set_xlabel('v [km\,s$^{-1}$]', fontsize=16)
        ax.set_ylabel('T$_\mathrm{b}$ [K]', fontsize=16)
        ax.set_axisbelow(True)
        ax.grid(color='gray', linestyle='dotted')
        ax.plot(cube.spectral_axis.value, [0. for i in cube.spectral_axis], color='gray', ls='-')
        ax.step(cube.spectral_axis.value, cube[:,y,x].value, where='mid', color='k')
        ax.axvline(247.5, color='turquoise', zorder=0)
        ax.set_xlim(0,500)
        ax.set_ylim( [[np.nanmin(cube[:,y,x].value)-0.1*i, 1.1*i] for i in [np.nanmax([np.abs(np.nanmin(cube[:,y,x].value)),np.nanmax(cube[:,y,x].value)])]][0] )
        fig.savefig(line_file.replace('fits','pdf'), dpi=300, transparent=True, bbox_inches='tight')

    else:
        print('Does not exist: '+line_file)


###################################################################################################
# execute line splitting
###################################################################################################

lsb_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.LSB.K.image.fits')
usb_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.USB.K.image.fits')
lsb_file_pbcor = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.LSB.K.image.pbcor.fits')
usb_file_pbcor = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.USB.K.image.pbcor.fits')

# get line list
lines = parse_line_list(os.path.join(projectdir,'NGC253.lines.band7.txt'))
lsb_lines = find_lines(lsb_file, lines)
usb_lines = find_lines(usb_file, lines)

# create mask templates
for im in [lsb_file, usb_file]:
    for w in [200,150,100,50,25]:
        mask_cube(image_file = im,
                   model_file = os.path.join(linedir,'diskfit.total_model.fits'),
                   modeldir   = 'diskfit',
                   width      = w*u.km/u.s
                  )
        mask_cube(image_file = im,
                   model_file = os.path.join(linedir,'CO_3-2.mom1.fits'),
                   modeldir   = 'CO_velocity',
                   width      = w*u.km/u.s
                  )
    mask_cube(image_file = im,
              model_file = os.path.join(linedir,'CO_3-2.cube.fits'),
              modeldir   = 'CO_treshold',
              threshold  = 3.5*u.K              # 10 sigma
             )
    mask_cube(image_file = im,
              model_file = os.path.join(linedir,'CO_3-2.cube.fits'),
              modeldir   = 'CO_treshold',
              threshold  = 1.0*u.K              # ~3 sigma
             )

# split out lines
for line in lsb_lines:
    for im in [lsb_file, lsb_file_pbcor]:
        for modeldir in ['diskfit','CO_velocity','CO_threshold']:
            split_line(image_file = im,
                       line       = line,
                       modeldir   = modeldir
                      )
for line in usb_lines:
    for im in [usb_file, usb_file_pbcor]:
        for modeldir in ['diskfit','CO_velocity','CO_threshold']:
            split_line(image_file = im,
                       line       = line,
                       modeldir   = modeldir
                      )

# get overview images
for line in lines:
    for modeldir in ['diskfit','CO_velocity','CO_threshold']:
        plot_spectrum(line, modeldir)
        plot_moment(line, modeldir)


####################################################################################################
