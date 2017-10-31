#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : ndk_2_obspydmt.py
Purpose : Make ndk cat file of events into obspydmt LOCAL file
Creation Date : 31-10-2017
Last Modified : Tue 31 Oct 2017 01:51:44 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from obspy import UTCDateTime


a = open('jan76_dec13.ndk','r').readlines()
one = a[0::5]
two = a[1::5]
three = a[2::5]
four = a[3::5]
five = a[4::5]
b = open('event_catalog.txt','w')


for idx,ii in enumerate(one):
    'DUR%4.1f EX %2d%6.2f%5.2f%6.2f%5.2f%6.2f%5.2f%6.2f%5.2f%6.2f%5.2f%6.2f%5.2f'
    ev_num = idx

    hype_ref = one[idx][0:4]
    date = one[idx][5:15]
    year = date.split('/')[0]
    month = date.split('/')[1]
    day = date.split('/')[2]
    time = one[idx][16:26]
    hour = time.split(':')[0]
    minute = time.split(':')[1]
    second = float(time.split(':')[2])
    lat = one[idx][27:33].strip()
    lon = one[idx][34:41].strip()
    h = one[idx][42:47].strip()
    mags = one[idx][48:55]
    mb = mags.strip().split()[0]
    ms = mags.strip().split()[1]
    loc = one[idx][56:80]

    ev_id = two[idx][0:16].strip()
    data = two[idx][17:61]
    source_type = two[idx][62:68]
    dur = two[idx][69:80]
    time = dur.strip().split(':')[-1].strip()

    cent_param = three[idx][0:58]
    type_depth = three[idx][59:63]
    timestamp = three[idx][64:80]

    exponent = four[idx][0:2]
    cmt_el = four[idx].strip().split()
    mrr = cmt_el[1]+'e+'+exponent
    mtt = cmt_el[3]+'e+'+exponent
    mpp = cmt_el[5]+'e+'+exponent
    mrt = cmt_el[7]+'e+'+exponent
    mrp = cmt_el[9]+'e+'+exponent
    mtp = cmt_el[11]+'e+'+exponent


    version_code = five[idx][0:3]

    if second >= 59.8:
        second = 59.8

    datetime = UTCDateTime(
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                float(second)
                )

    b.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
             ev_num,
             ev_id,
             datetime,
             lat,
             lon,
             h,
             mb,
             'MW',
             'None',
             'NAN',
             mrr,
             mtt,
             mpp,
             mrt,
             mrp,
             mtp,
             'triangle',
             time
             ))









