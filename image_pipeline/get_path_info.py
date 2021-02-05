
def get_path_info(filename):
    """
    Get the path and file name elements of an MS.

    Parameters
    ----------
    filename : string


    Returns
    -------
    strings

    """

    # aggregate name info
    if 'ms' in filename:
        source   = filename.split('.')[0]
        band     = filename.split('.')[1]
        array    = filename.split('.')[2]
        sideband = filename.split('.')[4]
        subdir = source+'.'+band+'.'+array+'.'+sideband+'/'
    elif 'image' in filename:
        source   = filename.split('.')[0]
        band     = filename.split('.')[1]
        array    = filename.split('.')[2]
        sideband = filename.split('.')[3]
        image_type = filename.split('.')[4]
    else:
        raise NameError("Cannot find out if measurement set or image.")

    if 'ms' in filename:
        return imagedir, subdir, source, band, array, sideband
    elif 'image' in filename:
        return imagedir, source, band, array, sideband, image_type
