

# # band 7, ACA, LSB
# image = '../012.lower_sideband/NGC253.band7.ACA.LSB.natural.deep.image.fits'
# line  = '*:342.180~342.320GHz;343.000~343.750GHz;344.300~344.750GHz'

# # band 7, 12m-mid, LSB
# image = '../012.lower_sideband/NGC253.band7.12m-mid.LSB.natural.dirty.image.fits'
# line  = '*:342.180~342.320GHz;343.000~343.700GHz;344.300~344.750GHz'

# band 7, 12m-high, LSB
image = '../012.lower_sideband/NGC253.band7.12m-high.LSB.natural.dirty.image.fits'
line  = '*:342.180~342.320GHz;343.000~343.750GHz;344.300~344.750GHz'



band     = image.split('/')[-1].split('.')[1]
array    = image.split('/')[-1].split('.')[2]
sideband = image.split('/')[-1].split('.')[3]
imtype   = image.split('/')[-1].split('.')[6]



# stats
stats = imstat(imagename=image, axes=[0,1])
sums  = stats['sum']*u.Jy
sums  = [s if s<1e6*u.Jy else np.nan*u.Jy for s in sums]

nchans = stats['trc'][2]
fmin = u.Quantity(stats['blcf'].split(', ')[2])
fmax = u.Quantity(stats['trcf'].split(', ')[2])
chans = np.arange(nchans+1)
chan_width = (fmax-fmin)/nchans
freqs = [chan*chan_width+fmin for chan in chans]

mask_ranges = [l[:-3].split('~') for l in line[2:].split(';')]
mask_ranges = [[float(f)*1e9 for f in x] for x in mask_ranges]


# plot
plt.ion()
fig,ax1 = plt.subplots()
ax1.plot([f.value for f in freqs], [s.value for s in sums], color='r', linestyle='-', label='sum')
ax1.plot(np.nan, color='b', label='mask')
for mask_true_range in mask_ranges:
    ax1.axvspan(mask_true_range[0], mask_true_range[1], color='b', alpha=0.5)
ax1.set_title(image.replace('_','\_'))
ax1.set_xlabel('frequency')
ax1.set_ylabel('flux [mJy]')
ax1.legend(loc='best')
ax1.set_xlim([fmin.value,fmax.value])
ax1.set_ylim([-5e3,5e3])
plt.show()
fig.savefig('plots/NGC253/900.various/contsub_control.'+band+'.'+array+'.'+sideband+'.png', dpi=300, transparent=True, bbox_inches='tight')
