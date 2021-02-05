####################################################################################################
# NGC 253 PROJECT INFO
####################################################################################################

# data setup
global projectdir; projectdir = 'XXXXX'
global logdir;     logdir     = os.path.join(projectdir,'logs')
global datadir;    datadir    = os.path.join(projectdir,'002.concat+contsub')
global imagedir;   imagedir   = os.path.join(projectdir,'004.imaging_robust')
global finaldir;   finaldir   = os.path.join(projectdir,'005.final_images')
global linedir;    linedir    = os.path.join(projectdir,'006.lines')


# NGC 253 details
global phasecenter; phasecenter = 'J2000 00h47m33.134 -25d17m19.68'
try:
    kin_center  = SkyCoord('00h47m33.134s -25d17m19.68s')
    cont_peak   = SkyCoord('00h47m33.297s -25d17m15.570s')
    distance    = 3.5*u.Mpc
    vsys        = 250*u.km/u.s
    inclination = 78*u.degree
    disk_PA     = 55.*u.degree
except:
    kin_center = '00h47m33.134 -25d17m19.68'

# plotting info
if 'aplpy_plotting' in sys.modules:
    ap.tick_label_xformat = 'hh:mm:ss.s'
    ap.tick_label_yformat = 'dd:mm:ss.s'
    ap.ticks_xspacing = Angle('0 0 1.0', unit='hourangle')
    ap.ticks_yspacing = 10.0*u.arcsec
    ap.ticks_minor_frequency = 5
    default_recenter = [SkyCoord('00h47m33.07s -25d17m20.0s'), 40.0*u.arcsec, 32.0*u.arcsec]
if 'easy_aplpy' in sys.modules:
    easy_aplpy.settings.tick_label_xformat = 'hh:mm:ss.s'
    easy_aplpy.settings.tick_label_yformat = 'dd:mm:ss.s'
    easy_aplpy.settings.ticks_xspacing = Angle('0 0 1.0', unit='hourangle')
    easy_aplpy.settings.ticks_yspacing = 10.0*u.arcsec
    easy_aplpy.settings.ticks_minor_frequency = 5
    default_recenter = [SkyCoord('00h47m33.07s -25d17m20.0s'), 40.0*u.arcsec, 32.0*u.arcsec]


###################################################################################################

# Raw datasets
##############

raw_datasets = [
#   {'name': 'NGC253.band6.TP.ms'},
    {'name': 'NGC253.band6.ACA.ms'},
    {'name': 'NGC253.band6.12m-mid.ms'},
    {'name': 'NGC253.band6.12m-high.ms'},
    {'name': 'NGC253.band7.TP.ms'},
    {'name': 'NGC253.band7.ACA.ms'},
    {'name': 'NGC253.band7.12m-mid.ms'},
    {'name': 'NGC253.band7.12m-high.ms'}
    ]


###################################################################################################

# Prepared datasets
###################

# These can be imaged

datasets = [
    {'name': 'NGC253.band6.TP.ms.LSB',       'restfreq': '218.0GHz', 'width': '3.5MHz', 'linefree': ''},
    {'name': 'NGC253.band6.TP.ms.USB',       'restfreq': '232.0GHz', 'width': '3.5MHz', 'linefree': ''},
    {'name': 'NGC253.band6.ACA.ms.LSB',      'restfreq': '218.0GHz', 'width': '3.5MHz', 'linefree': '0:0~50;210~245;475~510, 1:300~510, 2:70~100;260~320;820~950'},
    {'name': 'NGC253.band6.ACA.ms.USB',      'restfreq': '232.0GHz', 'width': '3.5MHz', 'linefree': '*:232.000~233.500GHz'},
    {'name': 'NGC253.band6.12m-mid.ms.LSB',  'restfreq': '218.0GHz', 'width': '3.5MHz', 'linefree': '2:216.250~216.400GHz,2:217.420~217.580GHz,1:219.130~219.250GHz'},
    {'name': 'NGC253.band6.12m-mid.ms.USB',  'restfreq': '232.0GHz', 'width': '3.5MHz', 'linefree': '*:232.000~233.500GHz'},
    {'name': 'NGC253.band6.12m-high.ms.LSB', 'restfreq': '218.0GHz', 'width': '3.5MHz', 'linefree': '2:216.150~216.300GHz;216.700~216.750GHz;217.100~217.150GHz;217.400~217.500GHz,1:218.28~218.33GHz;218.42~218.48GHz;218.85~218.92GHz;219.100~219.150GHz'},
    {'name': 'NGC253.band6.12m-high.ms.USB', 'restfreq': '232.0GHz', 'width': '3.5MHz', 'linefree': '*:232.000~233.500GHz'},
    {'name': 'NGC253.band7.TP.ms.LSB',       'restfreq': '344.0GHz', 'width': '2.5MHz', 'linefree': ''},
    {'name': 'NGC253.band7.TP.ms.USB',       'restfreq': '356.0GHz', 'width': '2.5MHz', 'linefree': ''},
    {'name': 'NGC253.band7.ACA.ms.LSB',      'restfreq': '344.0GHz', 'width': '2.5MHz', 'linefree': '0:700~1950, 2:700~1950, 4:700~1950, 6:700~1950, 8:700~1950, 10:700~1950, 12:700~1950, 14:700~1950, 16:700~1950, 18:700~1950, 20:700~1950, 21:700~1950, 23:700~1950, 25:700~1950, 28:700~1950, 30:700~1950, 32:700~1950, 34:700~1950, 36:700~1950, 38:700~1950, 40:700~1950, 42:700~1950, 43:700~1950, 45:700~1950, 47:700~1950, 50:700~1950, 52:700~1950, 1:100~1200;1620~1950, 3:100~1200;1620~1950, 5:100~1200;1620~1950, 7:100~1200;1620~1950, 9:100~1200;1620~1950, 11:100~1200;1620~1950, 13:100~1200;1620~1950, 15:100~1200;1620~1950, 17:100~1200;1620~1950, 19:100~1200;1620~1950, 22:100~1200;1620~1950, 24:100~1200;1620~1950, 26:100~1200;1620~1950, 27:100~1200;1620~1950, 29:100~1200;1620~1950, 31:100~1200;1620~1950, 33:100~1200;1620~1950, 35:100~1200;1620~1950, 37:100~1200;1620~1950, 39:100~1200;1620~1950, 41:100~1200;1620~1950, 44:100~1200;1620~1950, 46:100~1200;1620~1950, 48:100~1200;1620~1950, 49:100~1200;1620~1950, 51:100~1200;1620~1950, 53:100~1200;1620~1950'},
    {'name': 'NGC253.band7.ACA.ms.USB',      'restfreq': '356.0GHz', 'width': '2.5MHz', 'linefree': '0:750~1950, 1:750~1950, 3:750~1950, 6:750~1950, 8:750~1950, 10:750~1950, 11:750~1950, 13:750~1950, 16:750~1950, 18:750~1950, 20:750~1950, 22:750~1950, 24:750~1950, 26:750~1950, 28:750~1950, 30:750~1950, 32:750~1950, 33:750~1950, 35:750~1950, 38:750~1950, 40:750~1950, 42:750~1950, 44:750~1950, 46:750~1950, 48:750~1950, 50:750~1950, 52:750~1950, 2:80~450;1080~1950, 4:80~450;1080~1950, 5:80~450;1080~1950, 7:80~450;1080~1950, 9:80~450;1080~1950, 12:80~450;1080~1950, 14:80~450;1080~1950, 15:80~450;1080~1950, 17:80~450;1080~1950, 19:80~450;1080~1950, 21:80~450;1080~1950, 23:80~450;1080~1950, 25:80~450;1080~1950, 27:80~450;1080~1950, 29:80~450;1080~1950, 31:80~450;1080~1950, 34:80~450;1080~1950, 36:80~450;1080~1950, 37:80~450;1080~1950, 39:80~450;1080~1950, 41:80~450;1080~1950, 43:80~450;1080~1950, 45:80~450;1080~1950, 47:80~450;1080~1950, 49:80~450;1080~1950, 51:80~450;1080~1950, 53:80~450;1080~1950'},
    {'name': 'NGC253.band7.12m-mid.ms.LSB',  'restfreq': '344.0GHz', 'width': '2.5MHz', 'linefree': '0:850~1550, 1:100~650;1550~1900, 2:850~1550, 3:100~650;1550~1900, 4:850~1550, 5:100~650;1550~1900, 6:850~1550, 7:100~650;1550~1900'}, #'*:342.180~342.320GHz;343.000~343.700GHz;344.300~344.750GHz'},
    {'name': 'NGC253.band7.12m-mid.ms.USB',  'restfreq': '356.0GHz', 'width': '2.5MHz', 'linefree': '*:354.540~355.700GHz;356.030~356.260GHz;356.800~357.420GHz'},
    {'name': 'NGC253.band7.12m-high.ms.LSB', 'restfreq': '344.0GHz', 'width': '2.5MHz', 'linefree': '0:850~1600, 1:580~650;1570~1900, 2:850~1600, 3:580~650;1570~1900, 4:850~1600, 5:580~650;1570~1900, 6:850~1600, 7:580~650;1570~1900, 8:850~1600, 9:580~650;1570~1900'}, #'*:342.180~342.320GHz;343.000~343.750GHz;344.300~344.750GHz'},
    {'name': 'NGC253.band7.12m-high.ms.USB', 'restfreq': '356.0GHz', 'width': '2.5MHz', 'linefree': '*:354.000~354.100GHz;354.650~355.160GHz;355.500~355.680GHz;356.780~357.600GHz'}
    ]
datasets_contsub = copy.deepcopy(datasets)
for idx,entry in enumerate(datasets_contsub):
    if not ( 'TP' in entry['name']):
        datasets_contsub[idx]['name'] += '.contsub'

combined_datasets = [
    {'name': 'NGC253.band6.ACA+12m-mid+12m-high.ms.LSB', 'restfreq': '218.0GHz', 'width': '3.5MHz'},
    {'name': 'NGC253.band6.ACA+12m-mid+12m-high.ms.USB', 'restfreq': '232.0GHz', 'width': '3.5MHz'},
    {'name': 'NGC253.band6.ACA+12m-mid.ms.LSB',          'restfreq': '218.0GHz', 'width': '3.5MHz'},
    {'name': 'NGC253.band6.ACA+12m-mid.ms.USB',          'restfreq': '232.0GHz', 'width': '3.5MHz'},
    {'name': 'NGC253.band6.12m-mid+12m-high.ms.LSB',     'restfreq': '218.0GHz', 'width': '3.5MHz'},
    {'name': 'NGC253.band6.12m-mid+12m-high.ms.USB',     'restfreq': '232.0GHz', 'width': '3.5MHz'},
    {'name': 'NGC253.band7.ACA+12m-mid+12m-high.ms.LSB', 'restfreq': '344.0GHz', 'width': '2.5MHz'},
    {'name': 'NGC253.band7.ACA+12m-mid+12m-high.ms.USB', 'restfreq': '356.0GHz', 'width': '2.5MHz'},
    {'name': 'NGC253.band7.ACA+12m-mid.ms.LSB',          'restfreq': '344.0GHz', 'width': '2.5MHz'},
    {'name': 'NGC253.band7.ACA+12m-mid.ms.USB',          'restfreq': '356.0GHz', 'width': '2.5MHz'},
    {'name': 'NGC253.band7.12m-mid+12m-high.ms.LSB',     'restfreq': '344.0GHz', 'width': '2.5MHz'},
    {'name': 'NGC253.band7.12m-mid+12m-high.ms.USB',     'restfreq': '356.0GHz', 'width': '2.5MHz'}
    ]
combined_datasets_contsub = copy.deepcopy(combined_datasets)
for idx,entry in enumerate(combined_datasets_contsub):
    combined_datasets_contsub[idx]['name'] += '.contsub'


# all datasets prior to regridding
all_datasets_cont    = copy.deepcopy(datasets)         + copy.deepcopy(combined_datasets)
all_datasets_contsub = copy.deepcopy(datasets_contsub) + copy.deepcopy(combined_datasets_contsub)


###################################################################################################

# imageable datasets
####################

image_setups = [
    {'MS': 'NGC253.band6.TP.ms.LSB.regrid', 'imsize': 64, 'cell': 5.00*u.arcsec, 'linefree': ''},
    {'MS': 'NGC253.band6.TP.ms.USB.regrid', 'imsize': 64, 'cell': 5.00*u.arcsec, 'linefree': ''},
    {'MS': 'NGC253.band6.ACA.ms.LSB.contsub.regrid', 'imsize': 160, 'cell': 1.00*u.arcsec, 'linefree': '*:216.280~216.300GHz;217.420~217.480GHz;218.800~219.100GHz',
        'natural': {'noise': 3.80*u.mJy, 'major': 8.52*u.arcsec, 'minor': 4.33*u.arcsec, 'pa': 84.18*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.ACA.ms.USB.contsub.regrid', 'imsize': 160, 'cell': 1.00*u.arcsec, 'linefree': '*:232.000~233.500GHz',
        'natural': {'noise': 3.38*u.mJy,'major': 8.05*u.arcsec, 'minor': 4.12*u.arcsec, 'pa': 85.17*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.12m-mid.ms.LSB.contsub.regrid', 'imsize': 640, 'cell': 0.25*u.arcsec,  'linefree': '2:216.250~216.400GHz,2:217.420~217.580GHz,1:219.130~219.250GHz',
        'natural': {'noise': 1.38*u.mJy, 'major': 1.90*u.arcsec, 'minor': 1.03*u.arcsec, 'pa': 79.30*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.12m-mid.ms.USB.contsub.regrid', 'imsize': 640, 'cell': 0.25*u.arcsec, 'linefree': '*:232.000~233.500GHz',
        'natural': {'noise': 1.46*u.mJy, 'major': 1.77*u.arcsec, 'minor': 0.98*u.arcsec, 'pa': 79.38*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.12m-high.ms.LSB.contsub.regrid', 'imsize': 3200, 'cell': 0.05*u.arcsec, 'linefree': '2:216.150~216.300GHz;216.650~216.750GHz;217.050~217.150GHz;217.400~217.500GHz,1:219.100~219.150GHz',
        'natural': {'noise': 0.98*u.mJy,'major': 0.35*u.arcsec, 'minor': 0.23*u.arcsec, 'pa': 72.39*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.12m-high.ms.USB.contsub.regrid', 'imsize': 3200, 'cell': 0.05*u.arcsec,'linefree': '*:232.000~233.500GHz',
        'natural': {'noise': 1.53*u.mJy, 'major': 0.32*u.arcsec, 'minor': 0.22*u.arcsec, 'pa': 76.98*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.ACA+12m-mid.ms.LSB.contsub.regrid', 'imsize': 640, 'cell': 0.25*u.arcsec, 'linefree': '*:',
        'natural': {'noise': 6.65*u.mJy, 'major': 8.70*u.arcsec, 'minor': 4.47*u.arcsec, 'pa': 83.88*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.ACA+12m-mid.ms.USB.contsub.regrid', 'imsize': 640, 'cell': 0.25*u.arcsec, 'linefree': '*:',
        'natural': {'noise': 5.79*u.mJy, 'major': 8.22*u.arcsec, 'minor': 4.26*u.arcsec, 'pa': 84.43*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.12m-mid+12m-high.ms.LSB.contsub.regrid', 'imsize': 3200, 'cell': 0.05*u.arcsec, 'linefree': '*:',
        'natural': {'noise': 1.34*u.mJy,'major': 0.46*u.arcsec, 'minor': 0.34*u.arcsec, 'pa': 70.97*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.12m-mid+12m-high.ms.USB.contsub.regrid', 'imsize': 3200, 'cell': 0.05*u.arcsec, 'linefree': '*:',
        'natural': {'noise': 1.30*u.mJy, 'major': 0.42*u.arcsec, 'minor': 0.31*u.arcsec, 'pa': 76.49*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.ACA+12m-mid+12m-high.ms.LSB.contsub.regrid', 'imsize': 1280, 'cell': 0.10*u.arcsec, 'linefree': '*:',
        'natural': {'noise': 1.03*u.mJy, 'major': 0.83*u.arcsec, 'minor': 0.63*u.arcsec, 'pa': 72.94*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band6.ACA+12m-mid+12m-high.ms.USB.contsub.regrid', 'imsize': 1280, 'cell': 0.10*u.arcsec, 'linefree': '*:',
        'natural': {'noise': 0.97*u.mJy, 'major': 0.81*u.arcsec, 'minor': 0.60*u.arcsec, 'pa': 74.55*u.degree,},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },

    {'MS': 'NGC253.band7.TP.ms.LSB.regrid', 'imsize': 64, 'cell': 5.00*u.arcsec, 'linefree': ''},
    {'MS': 'NGC253.band7.TP.ms.USB.regrid', 'imsize': 64, 'cell': 5.00*u.arcsec, 'linefree': ''},
    {'MS': 'NGC253.band7.ACA.ms.LSB.contsub.regrid', 'imsize': 810,  'cell': 0.10*u.arcsec, 'linefree': '*:342.150~342.350GHz;342.850~343.750GHz;344.200~344.850GHz',
         'natural': {'noise': 3.80*u.mJy, 'major': 4.91*u.arcsec, 'minor': 3.01*u.arcsec, 'pa': -87.91*u.degree},
         'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band7.ACA.ms.USB.contsub.regrid', 'imsize': 810,  'cell': 0.10*u.arcsec, 'linefree': '*:354.500~356.150GHz;356.750~357.400GHz',
         'natural': {'noise': 4.65*u.mJy, 'major': 4.88*u.arcsec, 'minor': 2.91*u.arcsec, 'pa': 89.62*u.degree},
         'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band7.12m-mid.ms.LSB.contsub.regrid', 'imsize': 1620, 'cell': 0.05*u.arcsec, 'linefree': '*:342.140~342.400GHz;342.900~343.760GHz;344.200~344.830GHz',
        'natural': {'noise': 1.30*u.mJy, 'major': 0.41*u.arcsec, 'minor': 0.33*u.arcsec, 'pa': 87.05*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band7.12m-mid.ms.USB.contsub.regrid', 'imsize': 1620, 'cell': 0.05*u.arcsec, 'linefree': '*:354.540~355.700GHz;356.030~356.260GHz;356.800~357.420GHz',
         'natural': {'noise': 2.20*u.mJy, 'major': 0.44*u.arcsec, 'minor': 0.35*u.arcsec, 'pa': -87.57*u.degree},
         'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band7.12m-high.ms.LSB.contsub.regrid', 'imsize': 2700, 'cell': 0.03*u.arcsec, 'linefree': '*:342.150~342.450GHz;342.800~343.800GHz;344.190~344.900GHz',
        'natural': {'noise': 0.93*u.mJy, 'major': 0.17*u.arcsec, 'minor': 0.13*u.arcsec, 'pa': -72.04*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band7.12m-high.ms.USB.contsub.regrid', 'imsize': 2700, 'cell': 0.03*u.arcsec, 'linefree': '*:354.000~354.100GHz;354.650~355.160GHz;355.500~355.680GHz;356.780~357.600GHz',
        'natural': {'noise': 1.35*u.mJy, 'major': 0.16*u.arcsec, 'minor': 0.13*u.arcsec, 'pa': -69.68*u.degree},
        'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
    },
    {'MS': 'NGC253.band7.ACA+12m-mid.ms.LSB.contsub.regrid', 'imsize': 1620, 'cell': 0.05*u.arcsec, 'linefree': '*:',
            'natural': {'noise': 0.0*u.mJy, 'major': 0.00*u.arcsec, 'minor': 1.00*u.arcsec, 'pa': 0.00*u.degree},
            'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
        },
    {'MS': 'NGC253.band7.ACA+12m-mid.ms.USB.contsub.regrid', 'imsize': 1620, 'cell': 0.05*u.arcsec, 'linefree': '*:',
            'natural': {'noise': 0.0*u.mJy, 'major': 0.00*u.arcsec, 'minor': 1.00*u.arcsec, 'pa': 0.00*u.degree},
            'robust':  {'noise': 0.0*u.mJy, 'major': 0.0*u.arcsec, 'minor': 0.0*u.arcsec, 'pa': 0.0*u.degree}
        },
    {'MS': 'NGC253.band7.12m-mid+12m-high.ms.LSB.contsub.regrid', 'imsize': 1280, 'cell': 0.05*u.arcsec, 'linefree': '*:',
            'data range': [44,1505],
            'bad chans': [],
            'natural': {'noise': 0.00*u.mJy, 'major': 0.21*u.arcsec, 'minor': 0.17*u.arcsec, 'pa': 0.0000*u.degree},
            'robust':  {'noise': 0.81*u.mJy, 'major': 0.17*u.arcsec, 'minor': 0.13*u.arcsec, 'pa': -74.94*u.degree},
            'cutbox': '143,167,1215,1104'
        },
    {'MS': 'NGC253.band7.12m-mid+12m-high.ms.USB.contsub.regrid', 'imsize': 1280, 'cell': 0.05*u.arcsec, 'linefree': '*:',
            'data range': [45,1480],
            'bad chans': [],
            'natural': {'noise': 0.00*u.mJy, 'major': 0.21*u.arcsec, 'minor': 0.17*u.arcsec, 'pa': 0.0000*u.degree},
            'robust':  {'noise': 1.03*u.mJy, 'major': 0.17*u.arcsec, 'minor': 0.13*u.arcsec, 'pa': -73.32*u.degree},
            'cutbox': '143,167,1215,1104'
        },
    {'MS': 'NGC253.band7.ACA+12m-mid+12m-high.ms.LSB.contsub.regrid', 'imsize': 1280, 'cell': 0.05*u.arcsec, 'linefree': '*:',
            'data range': [44,1505],
            'bad chans': np.concatenate([range(0,45),range(757,774),range(1503,1555)]),
            'natural': {'noise': 0.72*u.mJy, 'major': 0.21*u.arcsec, 'minor': 0.17*u.arcsec, 'pa': -76.05*u.degree},
            'robust':  {'noise': 0.76*u.mJy, 'major': 0.17*u.arcsec, 'minor': 0.13*u.arcsec, 'pa': -73.62*u.degree},
            'cutbox': '126,148,1227,1117'
        },
    {'MS': 'NGC253.band7.ACA+12m-mid+12m-high.ms.USB.contsub.regrid', 'imsize': 1280, 'cell': 0.05*u.arcsec, 'linefree': '*:',
            'data range': [45,1503],
            'bad chans': np.concatenate([range(0,45),range(759,782),range(1504,1556)]),
            'natural': {'noise': 1.23*u.mJy, 'major': 0.21*u.arcsec, 'minor': 0.17*u.arcsec, 'pa': -75.14*u.degree},
            'robust':  {'noise': 0.98*u.mJy, 'major': 0.17*u.arcsec, 'minor': 0.13*u.arcsec, 'pa': -75.15*u.degree},
            'cutbox': '130,151,1221,1112'
        }
    ]


###################################################################################################
###################################################################################################
