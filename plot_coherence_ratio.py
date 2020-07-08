import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import re
from pandas.tseries.offsets import DateOffset

#Precip data
hearstcastle = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/Precip_HearstCastle_since20120101.csv',
                names = (['date','P']), parse_dates = ['date'])
hearstcastle.P = hearstcastle.P.fillna(0)

bigsur = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/Precip_BigSurStation_since20120101.csv',
                names = (['date','P']), parse_dates = ['date'])
bigsur.P = bigsur.P.fillna(0)

def water_year(df):
    breaks = list(df.index[(df['date'].dt.month == 10) & (df['date'].dt.day == 1)])
    breaks.append(len(df))
    df['cs'] = np.nan
    for start, end in zip(breaks[:-1], breaks[1:]):
        df.cs.iloc[start:end] = np.cumsum(df.P[start:end])
        df.cs.iloc[start] = np.nan

water_year(bigsur)
water_year(hearstcastle)

#ndvi
ndvi = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/NDVI.csv',parse_dates = [0]).set_index('date')

#radar
'''
ascending data
'''
asc_amp = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/asc_amp.csv', parse_dates = [0]).set_index('date')

asc_coh = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/asc_coh.csv', parse_dates = [0]).set_index('date')

asc_coh['rolling_avg'] = asc_coh.rel_mean.rolling('30D').mean()

'''
descending data
'''

desc_amp = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/desc_amp.csv', parse_dates = [0]).set_index('date')
desc_coh = pd.read_csv('/home/myja3483/Landslides/Bigsur/Results/desc_coh.csv', parse_dates = [0]).set_index('date')

desc_coh['rolling_avg'] = desc_coh.rel_mean.rolling('30D').mean()

#Plotting

#fig, (ax1, ax2) = plt.subplots(2,1,figsize = [15,8])
#ax1.plot(hearstcastle.date[(hearstcastle['date']>'2014-10-01')],
#    hearstcastle.cs[(hearstcastle['date']>'2014-10-01')], color = 'green',
#        label = 'Heart Castle Station')
fig, ax1 = plt.subplots(figsize = [15,5])
ax1.plot(bigsur.date[(bigsur['date']>'2014-10-01')],
    bigsur.cs[(bigsur['date']>'2014-10-01')], color = 'grey',
    label = 'Big Sur Station')
ax1.legend()
ax1.set_ylabel('Cumulative Precipitation [mm]', fontsize = 12)
ax1a = ax1.twinx()
#ax1a.axvline(mdates.date2num(datetime.strptime('2017-01-1','%Y-%m-%d')), color = 'k', lw = 6, alpha = 0.3)
#ax2.plot(asc_amp.date.values, asc_amp.rel_mean,'.', color = 'dodgerblue')
#ax1a.plot(asc_coh.rolling_avg, color = 'mediumpurple')
ax1a.plot(asc_amp.rel_mean,'^', color = 'k', markersize = 6 , markeredgecolor = 'k', alpha = 0.5, label = 'ascending orbit')
ax1a.plot(desc_amp.rel_mean,'v', color = 'k', markersize = 6, markeredgecolor = 'k', markerfacecolor = 'white', label = 'descending orbit')
ax1a.plot(ndvi.rel_mean,'+', color = 'red', markersize = 6, label = 'NDVI')
ax1a.axvline(mdates.date2num(datetime.strptime('2017-05-20','%Y-%m-%d')), color = 'grey', dashes = (5, 2))
ax1a.set_ylabel('Amplitude ratio, NDVI ratio', color = 'k', fontsize = 12)
#ax2.plot(bigsur.date[(bigsur['date']>'2014-10-01')],
#    bigsur.cs[(bigsur['date']>'2014-10-01')], color = 'royalblue',
#    label = 'Big Sur Station')
#ax1.plot(hearstcastle.date[(hearstcastle['date']>'2014-10-01')],
#    hearstcastle.cs[(hearstcastle['date']>'2014-10-01')], color = 'green',
#        label = 'Heart Castle Station')
#ax2.set_ylabel('Cumulative Precipitation [mm]')
#ax2a = ax2.twinx()
#ax2a.axvline(mdates.date2num(datetime.strptime('2017-01-1','%Y-%m-%d')), color = 'k', lw = 6, alpha = 0.3)
#ax2.plot(desc_amp['date'], desc_amp['mean'],'.', color = 'dodgerblue')
#ax2a.plot(desc_coh.rolling_avg, color = 'mediumpurple')
#ax2a.plot(ndvi.rel_mean,'.', color = 'darkorange', markersize = 10)
#ax2a.axvline(mdates.date2num(datetime.strptime('2017-05-20','%Y-%m-%d')), color = 'k', dashes = (5, 2))
#ax2a.set_ylabel('Amplitude Ratio', color = 'purple')
plt.title('Mud Creek amplitude ratio & NDVI')
ax1a.legend()
plt.tight_layout()
#plt.show()
plt.savefig('amplitude_ndvi.pdf')

'''
def two_scales(ax1, data1, data2, c1, c2):
    ax2 = ax1.twinx()
    ax1.plot(data1, color=c1)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('exp')
    ax2.plot(data2, color=c2)
    ax2.set_ylabel('sin')
    return ax1, ax2

fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10,4))
ax1, ax1a = two_scales(ax1, bigsur.cs[(bigsur['date']>'2014-10-01')], ndvi.rel_mean, 'royalblue', 'darkorange')
ax2, ax2a = two_scales(ax2, bigsur.cs[(bigsur['date']>'2014-10-01')], ndvi.rel_mean, 'royalblue', 'darkorange')


def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)

color_y_axis(ax1, 'r')
color_y_axis(ax1a, 'b')
color_y_axis(ax2, 'gold')
color_y_axis(ax2a, 'limegreen')

plt.tight_layout()
plt.show()
'''
