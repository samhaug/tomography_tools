#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : measure_crust_ttimes.py
Purpose : Measure ttimes as function of ray parameter for different crust
Creation Date : 08-04-2018
Last Modified : Wed 11 Apr 2018 12:05:40 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
import obspy
import argparse
from obspy.taup import TauPyModel
from scipy.signal import correlate
from glob import glob
model = TauPyModel(model='iasp91')

def main():
    parser = argparse.ArgumentParser(
                       description='measure_delays depending on crust')
    parser.add_argument('-s','--synth',metavar='N',type=str,
                        help='path to synthetic h5 streams')
    parser.add_argument('-d','--data',type=str,
                        help='stream of pure iasp91 synthetic',
                        default='/home/samhaug/work1/'\
                        'TOMO_synths/iasp91_pure/st_T.h5')
    args = parser.parse_args()
    st = obspy.read(args.data)
    st.sort(['gcarc'])
    st.interpolate(10)
    st.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    for idx,ii in enumerate(args.synth.split(',')):
        sts = obspy.read(ii)
        plot_ttimes(st,sts,label=ii)
    plt.grid()
    plt.legend()
    plt.show()

def plot_ttimes(st,sts,label):
    sts.sort(['gcarc'])
    sts.interpolate(10)
    sts.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    rp_list = []
    gcarc_list = []
    t_list = []
    ssrp_list = []
    sst_list = []
    for idx,tr in enumerate(st):
        #if tr.stats.gcarc > 30 and tr.stats.gcarc < 90:
        #    trs = sts[idx]
        #    rp,t = measure_ttime(trs,tr,'S')
        #    ssrp,sst = measure_ttime(trs,tr,'sS')
        #    rp_list.append(rp)
        #    ssrp_list.append(ssrp)
        #    gcarc_list.append(tr.stats.gcarc)
        #    t_list.append(t)
        #    sst_list.append(sst)
        if tr.stats.gcarc > 105 and tr.stats.gcarc < 150:
            trs = sts[idx]
            rp,t = measure_ttime(trs,tr,'Sdiff')
            ssrp,sst = measure_ttime(trs,tr,'sSdiff')
            rp_list.append(rp)
            ssrp_list.append(ssrp)
            gcarc_list.append(tr.stats.gcarc)
            t_list.append(t)
            sst_list.append(sst)
        else:
            continue

    t_list = np.array(t_list)
    sst_list = np.array(sst_list)
    #plt.scatter(gcarc_list,t_list*3-sst_list,label=label,alpha=0.5)
    plt.scatter(gcarc_list,t_list,label=label,alpha=0.5)
    #plt.scatter(gcarc_list,sst_list,label=label,alpha=0.5)
    #plt.show()

def measure_ttime(tr,trs,phase):
    evdp = tr.stats.evdp
    gcarc = tr.stats.gcarc
    arr = model.get_travel_times(source_depth_in_km=evdp,
                                 distance_in_degree=gcarc,
                                 phase_list=[phase])
    time = arr[0].time
    rp = arr[0].ray_param_sec_degree
    #rp = gcarc
    d = tr.slice(tr.stats.starttime+time-20,tr.stats.starttime+time+20).data
    s = trs.slice(tr.stats.starttime+time-20,tr.stats.starttime+time+20).data
    d *= 1./d.max()
    s *= 1./s.max()
    d += -1*d.mean()
    s += -1*s.mean()
    #if phase == 'SS':
        #plt.plot(d/d.max())
        #plt.plot(s/s.max())
        #plt.show()
    samp = tr.stats.sampling_rate
    del_t = npcorr(s,d,samp)
    print rp,del_t
    return rp,del_t

def npcorr(s,d,samp):
    correl = correlate(s,d,mode='same')
    ts = round((len(d)/2.-np.argmax(correl))/samp,2)
    return ts

main()
