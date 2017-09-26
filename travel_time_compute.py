#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : travel_time_compute.py
Purpose : Measure and record traveltime delays
Creation Date : 12-09-2017
Last Modified : Sun 24 Sep 2017 05:50:33 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

from numpy import round,argmax,max,abs,linspace,roll,pi,hstack,transpose,savetxt
from os import listdir,getcwd
from matplotlib import pyplot as plt
import obspy
from scipy.signal import correlate,butter,freqs
import argparse
from obspy.taup import TauPyModel
import time
model = TauPyModel(model='iasp91')


def main():
    parser = argparse.ArgumentParser(
                       description='Measure and record traveltime delays')
    parser.add_argument('-p','--phase',metavar='N',type=str,
                        help='Name of phase')
    parser.add_argument('-w','--window',default=30,type=int,
                        help='Half of the window length')
    parser.add_argument('--fmin',default=1./100,type=float,
                        help='Minimum frequency')
    parser.add_argument('--fmax',default=1./5,type=float,
                        help='Maximum frequency')
    parser.add_argument('-d','--data',type=str,
                        help='Path to data pickle')
    parser.add_argument('-s','--synth',type=str,
                        help='Path to synthetic pickle')
    parser.add_argument('--stride',default=1,type=int,
                        help='Use every Nth trace in stream')
    parser.add_argument('--plot',dest='plot',
                        action='store_true',help='Plot waveforms')
    args = parser.parse_args()
    fname = write_header(args.phase,args)
    amp_fname = write_amp_header(args.phase,args.fmin,args.fmax)
    branch_list = phase_info(args.phase)
    write_branch(fname,branch_list)
    write_f_resp(fname,args.fmin,args.fmax)
    std,sts = read_streams(args.data,args.synth)
    welcome_message(args,std)
    std,sts = phase_range(std,sts,args.phase)
    std.filter('bandpass',freqmin=args.fmin,freqmax=args.fmax,zerophase=True)
    sts.filter('bandpass',freqmin=args.fmin,freqmax=args.fmax,zerophase=True)
    now = time.time()
    for idx,ii in enumerate(range(0,len(std),args.stride)):
        total = len(range(0,len(std),args.stride))
        print '{}%'.format(round(float(idx)/total*100.))
        tobs,corcoeft,m1,m2,s_amp,d_amp,del_t,key=find_ttime(
                                       std[ii],sts[ii],[args.phase],
                                       (-1*args.window,args.window),args.plot)
        if key == 'control':
            write_traveltime(fname,std[ii],1.0,tobs,corcoeft,1.0,args.window,0)
            write_amplitude(amp_fname,std[ii],1.0,tobs,corcoeft,m1,
                            m2,s_amp,d_amp,del_t)
        else:
            continue
    then = time.time()
    rate = (len(std)/args.stride)/(then-now)
    print 'Total time: {} sec\n'.format(then-now)
    print 'Your rate: {} traces/sec\n'.format(rate)

def welcome_message(args,st):
    print('#######################################')
    print('Computing and recording traveltime delays')
    print('#######################################')
    print 'Data file: ',args.data
    print 'Synthetic file: ',args.synth
    print 'Number of traces: ',len(st)
    print 'Measuring delay of phase ',args.phase
    print 'Event depth: {}km'.format(str(st[0].stats.sac['evdp']))
    print 'Phase window is {} seconds long'.format(2*args.window)
    print 'Butterworth filter from {} Hz to {} Hz'.format(args.fmin,args.fmax)
    print 'Using every {} traces'.format(args.stride)
    if args.plot:
        print('Plotting is on')
    if args.plot != True:
        print('Plotting is off')
    print('#######################################')

def find_ttime(data_tr,synth_tr,phase,window_tuple,plot):
    samp = data_tr.stats.sampling_rate
    d_o = data_tr.stats.sac['o']
    d_st = data_tr.stats.starttime
    s_o = synth_tr.stats.sac['o']
    s_st = synth_tr.stats.starttime
    time = model.get_travel_times(source_depth_in_km=data_tr.stats.sac['evdp'],
                                  distance_in_degree=data_tr.stats.sac['gcarc'],
                                  phase_list=phase)[0].time
    d = data_tr.slice(d_st+time+d_o+window_tuple[0],
                      d_st+time+d_o+window_tuple[1]).data
    s = synth_tr.slice(s_st+time+s_o+window_tuple[0],
                       s_st+time+s_o+window_tuple[1]).data
    tobs = (len(d)/2.-argmax(correlate(s,d,mode='same')))/samp+time
    tobs = round(tobs,2)
    m1 = round(max(correlate(d,s))/max(correlate(s,s)),3)
    m2 = round(max(correlate(d,d))/max(correlate(d,s)),3)
    corcoeft = round(1-(m2-m1),3)
    s_amp = round(max(abs(s)),1)
    d_amp = round(max(abs(d)),1)
    del_t = round(tobs-time,2)

    if plot == True:
        class ClickSelect(object):
            def __init__(self):
                self.key = None
                fig = plt.gcf()
                fig.canvas.mpl_connect('key_press_event', self.on_key)
            def on_key(self,event):
                self.key = event.key
                plt.close()
                return True

        fig,ax = plt.subplots(2,1)
        plt.figtext(0.1,0.95,'press ctrl to save')
        t = linspace(window_tuple[0],window_tuple[1],num=len(d))
        td_full = linspace(0,data_tr.stats.endtime-data_tr.stats.starttime,num=data_tr.stats.npts)
        ts_full = linspace(0,data_tr.stats.endtime-data_tr.stats.starttime,num=synth_tr.stats.npts)
        ax[1].plot(td_full,data_tr.data/data_tr.data.max(),color='k')
        ax[1].plot(ts_full,synth_tr.data/synth_tr.data.max()+1,color='r')
        ax[1].set_xlim(time+synth_tr.stats.sac['o']-200,time+synth_tr.stats.sac['o']+200)
        ax[1].set_ylim(-1.5,2.5)
        ax[0].plot(t,d,color='k')
        ax[0].plot(t,s,color='r')
        ax[0].plot(t,roll(s,int(samp*(del_t))),color='r',ls='--')
        ax[0].plot(t,roll(s,int(samp*(del_t+1))),color='b',ls='--',alpha=0.3)
        ax[0].plot(t,roll(s,int(samp*(del_t-1))),color='g',ls='--',alpha=0.3)
        ax[0].set_xlabel('Time (s)')
        ax[0].set_title('M1:{} \nM2:{} \ndel_t:{} \ndel_amp:{}\n gcarc:{}'.format(
                     str(m1),str(m2),str(del_t),str(s_amp-d_amp),
                     str(data_tr.stats.sac['gcarc'])))
        clicks = ClickSelect()
        plt.show()
    return tobs,corcoeft,m1,m2,s_amp,d_amp,del_t,clicks.key

def read_streams(data_pickle,synth_pickle):
    sts = obspy.read(synth_pickle)
    std = obspy.read(data_pickle)
    sts.sort(['station'])
    std.sort(['station'])
    sts.interpolate(10)
    std.interpolate(10)
    return std,sts

def write_traveltime(fname,tr,tsig,tobs,corcoeft,nbt,xcl,tincore):
    idate=str(tr.stats.starttime.year)[-2::]+'%03d'%tr.stats.starttime.day
    iotime='%02d%02d%02d'%(tr.stats.starttime.hour,
                           tr.stats.starttime.minute,
                           tr.stats.starttime.second)
    ievt='1'
    kluster='0'
    stationcode=tr.stats.station
    netw=tr.stats.network
    comp=tr.stats.channel
    slat=round(tr.stats.sac['evla'],2)
    slon=round(tr.stats.sac['evlo'],2)
    sdep=round(tr.stats.sac['evdp'],2)
    rlat=round(tr.stats.sac['stla'],2)
    rlon=round(tr.stats.sac['stlo'],2)
    relev=0.0
    nobst=1
    nobsa=0
    #number of polar crossings
    kpole=0
    line_2 = '1 0 00\n'
    line_3 = '1\n'
    line_5 = '0\n'
    with open(fname,'a') as f:
        f.write('{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'.format(
                str(idate),
                str(iotime),
                str(ievt),
                str(kluster),
                stationcode,
                netw,
                comp,
                str(slat),
                str(slon),
                str(sdep),
                str(rlat),
                str(rlon),
                str(relev),
                str(nobst),
                str(nobsa),
                str(kpole),
                ))
        f.write(line_2)
        f.write(line_3)
        f.write('{} {} {} {} {} {}\n'.format(
                 str(tobs),
                 str(tsig),
                 str(corcoeft),
                 str(int(nbt)),
                 str(2.*xcl),
                 str(int(tincore))))
        f.write(line_5)

def write_header(phase_name,args):
    fmin = str(args.fmin)
    fmax = str(args.fmax)
    fname = getcwd().split('/')[-1]+'_'+phase_name+'_'+fmin+'_'+fmax+'.dat'
    with open(fname,'w') as f:
        f.write(fname+'\n')
        f.write('None\n')
    return fname

def write_f_resp(fname,fmin,fmax):
    fmin *= 2*pi
    fmax *= 2*pi
    b,a = butter(4,(fmin,fmax),'bandpass',analog=True)
    w,h = freqs(b, a)
    w = round(w,5)
    h = abs(round(h,5))
    freq_resp = hstack((transpose([w]),transpose([h])))
    with open(fname,'a') as f:
        f.write('1\n')
        f.write('{}\n'.format(len(w)))
        savetxt(f,freq_resp,fmt='%1.7f')

def write_branch(fname,branch_list):
    with open(fname,'a') as f:
        for ii in branch_list:
            f.write(ii+'\n')

def phase_info(phase_name):
    if phase_name == 'sSdiff':
        branch_list = ['sSdiff','sSdiff','DONT USE','DONT USE','DONT USE']
    if phase_name == 'Sdiff':
        branch_list = ['Sdiff','Sdiff','DONT USE','DONT USE','DONT USE']
    if phase_name == 'S':
        branch_list = ['S','S','6371 1 2','3482 2 2','6371 5 0']
    elif phase_name == 'sS':
        branch_list = ['sS','sS','6300 0 2','6371 1 2','3482 3 2','6371 5 0']

    elif phase_name == 'ScS':
        branch_list = ['ScS','ScS','6371 1 2','3482 3 2','6371 5 0']
    elif phase_name == 'ScSScS':
        branch_list = ['ScSScS','ScSScS','6371 1 2','3482 3 2','6371 3 2','3482 3 2','6371 5 0']

    elif phase_name == 'SS':
        branch_list = ['SS','SS','6371 0 2','3482 2 2','6371 3 2','3482 2 2','6371 5 0']
    else:
        print('Phase name first argument')
    return branch_list

def phase_range(std,sts,phase_name):
    if phase_name == 'Sdiff' or phase_name == 'sSdiff':
        for tr in std:
            if tr.stats.sac['gcarc'] > 160.:
                std.remove(tr)
            if tr.stats.sac['gcarc'] < 105.:
                std.remove(tr)
        for tr in sts:
            if tr.stats.sac['gcarc'] > 160.:
                sts.remove(tr)
            if tr.stats.sac['gcarc'] < 105.:
                sts.remove(tr)
    if phase_name == 'S' or phase_name == 'sS':
        for tr in std:
            if tr.stats.sac['gcarc'] > 95.:
                std.remove(tr)
            if tr.stats.sac['gcarc'] < 5.:
                std.remove(tr)
        for tr in sts:
            if tr.stats.sac['gcarc'] > 95.:
                sts.remove(tr)
            if tr.stats.sac['gcarc'] < 5.:
                sts.remove(tr)
    if phase_name == 'ScS' or phase_name == 'sScS':
        for tr in std:
            if tr.stats.sac['gcarc'] > 60.:
                std.remove(tr)
        for tr in sts:
            if tr.stats.sac['gcarc'] > 60.:
                sts.remove(tr)
    if phase_name == 'ScSScS' or phase_name == 'sScSScS':
        for tr in std:
            if tr.stats.sac['gcarc'] > 80.:
                std.remove(tr)
        for tr in sts:
            if tr.stats.sac['gcarc'] > 80.:
                sts.remove(tr)
    if phase_name == 'SS' or phase_name == 'sSS':
        for tr in std:
            if tr.stats.sac['gcarc'] > 175.:
                std.remove(tr)
            if tr.stats.sac['gcarc'] < 40.:
                std.remove(tr)
        for tr in sts:
            if tr.stats.sac['gcarc'] > 175.:
                sts.remove(tr)
            if tr.stats.sac['gcarc'] < 40.:
                sts.remove(tr)

    return std,sts

def write_amp_header(phase_name,fmin,fmax):
    fname = getcwd().split('/')[-1]+'_'+phase_name+'_amp.dat'
    with open(fname,'w') as f:
        f.write(fname+'\n')
        f.write('fmin,fmax''\n')
        f.write('{} {}\n'.format(fmin,fmax))
        f.write('idate,iotime,stat,netw,comp,slat,slon,sdep,rlat,rlon,relev,tobs,delt,corcoeft,m1,m2,s_amp,d_amp\n')
    return fname

def write_amplitude(fname,tr,tsig,tobs,corcoeft,m1,m2,s_amp,d_amp,del_t):
    idate=str(tr.stats.starttime.year)[-2::]+'%03d'%tr.stats.starttime.day
    iotime='%02d%02d%02d'%(tr.stats.starttime.hour,
                           tr.stats.starttime.minute,
                           tr.stats.starttime.second)
    stationcode=tr.stats.station
    netw=tr.stats.network
    comp=tr.stats.channel
    slat=round(tr.stats.sac['evla'],2)
    slon=round(tr.stats.sac['evlo'],2)
    sdep=round(tr.stats.sac['evdp'],2)
    rlat=round(tr.stats.sac['stla'],2)
    rlon=round(tr.stats.sac['stlo'],2)
    relev=0
    #number of polar crossings
    line_2 = '1 0 00\n'
    line_3 = '1\n'
    line_5 = '0\n'
    with open(fname,'a') as f:
        f.write('{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'.format(
                str(idate),
                str(iotime),
                stationcode,
                netw,
                comp,
                str(slat),
                str(slon),
                str(sdep),
                str(rlat),
                str(rlon),
                str(relev),
                str(tobs),
                str(del_t),
                str(corcoeft),
                str(m1),
                str(m2),
                str(s_amp),
                str(d_amp)
                ))

main()

