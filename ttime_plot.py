#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : ttime_plot.py
Purpose : ---
Creation Date : 08-04-2018
Last Modified : Mon 09 Apr 2018 10:04:26 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from subprocess import call
from os import listdir
import obspy
from obspy.taup import TauPyModel
model = TauPyModel(model='prem')
import argparse

def main():
    parser = argparse.ArgumentParser(
                       description='make traveltime table')
    parser.add_argument('-d','--evdp',metavar='N',type=int,
                        help='event depth')
    args = parser.parse_args()
    fig,ax = setup_figure()
    s_list = []
    scs_list = []
    sdiff_list = []
    for ii in np.linspace(10,180,num=170):
        arr_S = model.get_travel_times(source_depth_in_km=args.evdp,
                                       distance_in_degree=ii,
                                       phase_list=['S'])
        if len(arr_S) != 0:
            s_list.append((ii,arr_S[0].time))

        arr_Sdiff = model.get_travel_times(source_depth_in_km=args.evdp,
                                       distance_in_degree=ii,
                                       phase_list=['Sdiff'])
        if len(arr_Sdiff) != 0:
            sdiff_list.append((ii,arr_Sdiff[0].time))

        arr_ScS = model.get_travel_times(source_depth_in_km=args.evdp,
                                       distance_in_degree=ii,
                                       phase_list=['ScS'])
        if len(arr_ScS) != 0:
            scs_list.append((ii,arr_ScS[0].time))
    s_list = np.array(s_list)
    scs_list = np.array(scs_list)
    sdiff_list = np.array(sdiff_list)
    ax.plot(s_list[:,0],s_list[:,1])
    ax.plot(scs_list[:,0],scs_list[:,1])
    ax.plot(sdiff_list[:,0],sdiff_list[:,1])
    plt.show()

def setup_figure():
    fig,ax = plt.subplots(figsize=(5,9))
    ax.grid()
    ax.set_xlim(0,180)
    return fig,ax


main()
