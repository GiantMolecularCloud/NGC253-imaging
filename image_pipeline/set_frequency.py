def set_frequency(band):

    if ( band == 'band6' ):
        chanwidth = 3.5*u.MHz
        if ( 'LSB' in MS_file ):
            restfreq = '218.0GHz'
        elif ( 'USB' in MS_file ):
            restfreq = '232.0GHz'
    elif ( band == 'band7' ):
        chanwidth = 2.5*u.MHz
        if ( 'LSB' in MS_file ):
            restfreq = '344.0GHz'
        elif ( 'USB' in MS_file ):
            restfreq = '356.0GHz'

    return chanwidth, restfreq
