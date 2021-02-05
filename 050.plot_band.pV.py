############
# PLOTTING #
############

# Show large pV diagram highlighting the bright and faint lines in this dataset.


###################################################################################################
# project info
###################################################################################################

execfile('NGC253/project_info.py')

LSB_file    = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.LSB.K.image.fits')
USB_file    = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.USB.K.image.fits')
LSB_pVf_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.LSB.K.pV.full.fits')
LSB_pVm_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.LSB.K.pV.major.fits')
USB_pVf_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.USB.K.pV.full.fits')
USB_pVm_file = os.path.join(finaldir,'NGC253.band7.TP+12m-mid+12m-high.USB.K.pV.major.fits')
plotdir     = 'plots/NGC253/050.pV/'


###################################################################################################
# load data
###################################################################################################

LSB = SpectralCube.read(LSB_file)
USB = SpectralCube.read(USB_file)


###################################################################################################
# generate pV in pvextractor
###################################################################################################

from pvextractor import PathFromCenter
from pvextractor import extract_pv_slice

full = PathFromCenter(center=kin_center, length=60*u.arcsec, angle=disk_PA, width=30*u.arcsec)
maj  = PathFromCenter(center=kin_center, length=60*u.arcsec, angle=disk_PA, width=1*u.arcsec)

LSB_pV_full = extract_pv_slice(LSB, full)
LSB_pV_maj  = extract_pv_slice(LSB, maj)
USB_pV_full = extract_pv_slice(USB, full)
USB_pV_maj  = extract_pv_slice(USB, maj)

# offset is in degrees, frequency in Hz
# convert to reasonable units
# shift offset axis so that 0 corresponds to the kinematic center
for h in [LSB_pV_full.header, LSB_pV_maj.header, USB_pV_full.header, USB_pV_maj.header]:
    h['crval1'] *= 60*60
    h['cdelt1'] *= 60*60
    h['cunit1'] =  'arcsec'
    h['crval2'] /= 1e9
    h['cdelt2'] /= 1e9
    h['cunit2'] =  'GHz'
    h['crval1'] = 0.
    h['crpix1'] = int(np.round(h['naxis1']/2., 0))

LSB_pV_full.writeto(LSB_pVf_file, overwrite=True)
LSB_pV_maj.writeto(LSB_pVm_file, overwrite=True)
USB_pV_full.writeto(USB_pVf_file, overwrite=True)
USB_pV_maj.writeto(USB_pVm_file, overwrite=True)


###################################################################################################
# plot pV
###################################################################################################

easy_aplpy.settings.ticks_xspacing = 10.0*u.arcsec
easy_aplpy.settings.ticks_yspacing = 0.5*u.GHz
easy_aplpy.settings.ticks_minor_frequency = 5

for SB,sb,p in [(LSB_pVf_file,'LSB','full'),(LSB_pVm_file,'LSB','major'),(USB_pVf_file,'USB','full'),(USB_pVm_file,'USB','major')]:

    easy_aplpy.plot.map(SB,
        figsize   = (8,16),
        cmap      = 'Blues', #easy_aplpy.custom_colormaps.viridis_cropped,
        stretch   = 'linear',
        vmin      = -0.05,
        vmax      = 0.5,
        # recenter  = [ocen, fcen, oran, fran],
        contours  = [[SB, [2,4,8,16,32,64], 'black']],
        colorbar  = ['right', 'T$_{\mathrm{b}}$ [K]'],
        labels    = [r'offset along major axis (west to east) [$^{\prime\prime}$]', r'Frequency [GHz]'],
        out       = os.path.join(plotdir, sb+'.pV.'+p+'.pdf')
        )

    # recenter does not work with pV diagrams. Aplpy somehow always uses Hz for the spectral axis
    # and then messes up its internal Hz with the GHz of the image WCS.

    # h = fits.getheader(SB)
    # omin = (length/2.)*-1
    # omax = (length/2.)
    # ocen = (omin+omax)/2.
    # oran = omax-omin/2.
    # fmin = u.Quantity(str((h['crpix2']+0)*h['cdelt2']+h['crval2'])+h['cunit2'])
    # fmax = u.Quantity(str((h['crpix2']+h['naxis2'])*h['cdelt2']+h['crval2'])+h['cunit2'])
    # fcen = (fmin+fmax)/2.
    # fran = fmax-fmin/2.

###################################################################################################
