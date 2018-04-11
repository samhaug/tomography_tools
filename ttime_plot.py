#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : ttime_plot.py
Purpose : ---
Creation Date : 08-04-2018
Last Modified : Wed 11 Apr 2018 04:56:45 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from subprocess import call
from os import listdir
import obspy
from obspy.taup import TauPyModel
model = TauPyModel(model='iasp91')
import argparse

def main():
    parser = argparse.ArgumentParser(
                       description='make traveltime table')
    parser.add_argument('-d','--evdp',metavar='N',type=int,
                        help='event depth')
    args = parser.parse_args()
    fig,ax = setup_figure()
    for ii in np.arange(0,750,50):
        plot_depth(ii,ax)
    plt.show()
    plt.savefig('ttime_plot.pdf')

def plot_depth(evdp,ax):
    print evdp
    s_list = []
    scs_list = []
    sdiff_list = []
    ss_list = []
    sss_list = []
    scs2_list = []
    for ii in np.arange(80,110,0.25):
        arr_SSS = model.get_travel_times(source_depth_in_km=evdp,
                                       distance_in_degree=ii,
                                       phase_list=['SSS'])
        if len(arr_SSS) != 0:
            sss_list.append((ii,arr_SSS[0].time))

        arr_SS = model.get_travel_times(source_depth_in_km=evdp,
                                       distance_in_degree=ii,
                                       phase_list=['SS'])
        if len(arr_SS) != 0:
            ss_list.append((ii,arr_SS[0].time))

        arr_S = model.get_travel_times(source_depth_in_km=evdp,
                                       distance_in_degree=ii,
                                       phase_list=['S'])
        if len(arr_S) != 0:
            s_list.append((ii,arr_S[0].time))

        arr_Sdiff = model.get_travel_times(source_depth_in_km=evdp,
                                       distance_in_degree=ii,
                                       phase_list=['Sdiff'])
        if len(arr_Sdiff) != 0:
            sdiff_list.append((ii,arr_Sdiff[0].time))

        arr_ScS = model.get_travel_times(source_depth_in_km=evdp,
                                       distance_in_degree=ii,
                                       phase_list=['ScS'])
        if len(arr_ScS) != 0:
            scs_list.append((ii,arr_ScS[0].time))

        arr_ScS2 = model.get_travel_times(source_depth_in_km=evdp,
                                       distance_in_degree=ii,
                                       phase_list=['ScSScS'])
        if len(arr_ScS2) != 0:
            scs2_list.append((ii,arr_ScS2[0].time))

    s_list = np.array(s_list)
    scs_list = np.array(scs_list)
    scs2_list = np.array(scs2_list)
    sdiff_list = np.array(sdiff_list)
    ss_list = np.array(ss_list)
    sss_list = np.array(sss_list)
    ax.plot(s_list[:,0],s_list[:,1],color='k')
    ax.plot(scs_list[:,0],scs_list[:,1],color='b')
    ax.plot(scs2_list[:,0],scs2_list[:,1],color='orange')
    ax.plot(sdiff_list[:,0],sdiff_list[:,1],color='r')
    ax.plot(ss_list[:,0],ss_list[:,1],color='g')
    ax.plot(sss_list[:,0],sss_list[:,1],color='purple')

def setup_figure():
    fig,ax = plt.subplots(figsize=(5,9))
    ax.grid()
    ax.set_xlim(0,180)
    return fig,ax


main()
