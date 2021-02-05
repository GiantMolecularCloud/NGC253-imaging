def get_image_info(filename):
    """
    Get info about image setup.

    Parameters
    ----------
    filename : string
        File nam of measurement set.

    Returns
    -------
    various types
        Returns index of info in table image_setups, imsize, cell, noise, major, minor and pa beam info.

    """

    if 'ms' in filename:
        MS_idx = get_idx(image_setups, filename, key='MS')
        imsize = image_setups[MS_idx]['imsize']
        cell   = image_setups[MS_idx]['cell']
        try:
            noise  = image_setups[MS_idx]['robust']['noise']
            major  = image_setups[MS_idx]['robust']['major']
            minor  = image_setups[MS_idx]['robust']['minor']
            pa     = image_setups[MS_idx]['robust']['pa']
        except:
            noise = None
            major = None
            minor = None
            pa    = None

        return MS_idx, imsize, cell, noise, major, minor, pa

    elif '.fits' in filename:
        header = fits.open(filename)[0].header
        data   = fits.open(filename)[0].data

        imsize = header['naxis1']
        cell   = (header['cdelt1']*u.rad).to(u.arcsec)
        major  = (header['bmaj']*u.rad).to(u.arcsec)
        minor  = (header['bmin']*u.rad).to(u.arcsec)
        pa     = header['bpa']*u.deg

        noises = [np.sqrt(np.nanmean(d**2)) for d in data]
        noise  = (np.nanmedian(noises)*u.Jy).to(u.mJy)

        return imsize, cell, noise, major, minor, pa
