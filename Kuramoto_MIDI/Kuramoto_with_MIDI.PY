# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 14:03:36 2018

@author: Chris
"""

import Kuramoto as Kuramoto
import Functions
from mido import Message, MidiFile, MidiTrack, MetaMessage, frozen
import mido as mido
import pylab as plt
import numpy as np
from numpy.random import normal
import math 

plt.close(0)
plt.close(1)
plt.close(2)
plt.close(3)
plt.close(4)

class Kuramoto_with_MIDI():
    
    def __init__(self, Input_MIDI_File):
        self.mid = Input_MIDI_File
    
    MIDI_phases = []
    MIDI_times = []
    tempo = 0
    frequency = 0
    oscN = 0
    OSC_phases = []
    OSC_times = []
    output_MIDI_phases = []
    output_MIDI_times = []
    
    def get_MIDI_phases_and_times(self):
        self.tempo, self.frequency = Functions.get_tempo_and_frequency(self.mid.tracks[0])
        
        self.MIDI_phases, self.MIDI_times = Functions.get_MIDI_phases_and_times(self.mid, self.tempo, self.frequency) 
        
        plt.figure(0)
        for i in range(len(self.MIDI_times)): 
            plt.scatter(self.MIDI_times[i], self.MIDI_phases[i])
        plt.show(0)
    
    
    def run_kuramoto(self, _K = np.ones(shape = (25,25)), _K2 = np.ones(shape = (25,25)), scaling_factor = 1):
        t0, dt = 0, 0.001
        t1 = 0
        
        self.get_MIDI_phases_and_times()
        
        for mytimes in self.MIDI_times:
            if len(mytimes) > 0 and np.amax(mytimes) > t1:
                t1 = np.amax(mytimes)    

        T = np.arange(t0, t1, dt)
        
        _Y0 = np.array(np.zeros(len(self.mid.tracks)))
        
        _W = []
        for i in range(len(self.mid.tracks)):
            _W.append((normal(self.frequency, scale=0.1)*(2*math.pi)))
            
        _K = np.dstack((_K, _K2)).T*scaling_factor
        
        # Preparing oscillators with Kuramoto model
        self.oscN = len(self.mid.tracks) # num of oscillators
        
        Y0 = _Y0[:self.oscN]
        W = _W[:self.oscN]
        K = _K[:,:self.oscN,:self.oscN]

        init_params = {'W':W, 'K':K, 'Y0':Y0}

        kuramoto = Kuramoto.Kuramoto(init_params)
        kuramoto.noise = 'normal'
        odePhi = kuramoto.solve(T)
        odeT = T[:-1]
        
        plt.figure(1)

        for comp in range(len(W)):
            #plt.subplot(len(W),1,comp+1)
            plt.plot(odeT, np.diff(odePhi[comp])/dt)
            plt.ylabel('$\dot\phi(t)$   $(rad/sec)$')
            plt.xlabel('Time (secs)')
        
        plt.suptitle("Instantaneous frequencies")
        plt.savefig('phases')

        # Display plot
        plt.show(1)
    
        plt.figure(2)
        for i in range(len(W)):
            phases = []
            times = []
            time = 0
        
            dphidt = (np.diff(odePhi[i])/dt)
            j = 0
            for phi in odePhi[i]:

                phases.append(math.ceil(phi*100)/100)  # Round to two decimals
            
                time = ((phi)/((dphidt[j-1])))
                times.append(time)
                j+=1
            
            self.OSC_phases.append(phases)
            self.OSC_times.append(times)
                         
            plt.plot(T, self.OSC_phases[i])
            plt.ylabel('$\Theta$   (radians)')
            plt.xlabel('Time (Secs)')
            plt.suptitle("Cumulative Phase")
        
        plt.suptitle("Phases")
    
        #Display plot
        plt.show(2)
    
        plt.figure(3)
        instant_freqs = []
        for i in range(len(self.mid.tracks)):
            instant_freqs.append(np.diff(odePhi[i])/dt)

        self.output_MIDI_phases, output_midi_instant_freq = Functions.compute_output_kuramoto_phases(self.MIDI_phases, self.OSC_phases, self.frequency, instant_freqs)

        self.output_MIDI_times = Functions.compute_output_kuramoto_times(self.output_MIDI_phases, output_midi_instant_freq)
  
        for i in range(len(self.output_MIDI_times)):
            plt.scatter(self.output_MIDI_times[i], self.output_MIDI_phases[i])

        plt.show(3)
        
        track_number = 0
        temp_time = 0

        for track in self.mid.tracks:
            note = 0
            temp_time = 0
            for msg in track:
                if msg.type == 'note_on': 
                    msg.time = abs(int(mido.second2tick((self.output_MIDI_times[track_number][note] - temp_time), self.mid.ticks_per_beat, self.tempo)))
                    temp_time = self.output_MIDI_times[track_number][note]
                    note +=1    # Note counter must be in "if" statement
            track_number +=1
        
#        plt.figure(4)
#        
#        plt.scatter(self.output_MIDI_times[5], self.output_MIDI_phases[5])
#        plt.scatter(self.MIDI_times[5], self.MIDI_phases[5])
#
#        plt.show(4)
    
        KuramotoMIDI = MidiFile(type = 1)

        for track in self.mid.tracks:
            KuramotoMIDI.tracks.append(track)

        KuramotoMIDI.ticks_per_beat = self.mid.ticks_per_beat

        return KuramotoMIDI



#%% Main

#mid = MidiFile('LITEGROO.MID')
#
#MIDI_data = open('MIDI_data.txt', 'w')
#Out_MIDI_data = open('Out_MIDI_data.txt', 'w')
#
#for track in mid.tracks:
#    for msg in track:
#        MIDI_data.write("{0}\n".format(msg))
#
#x = Kuramoto_with_MIDI(mid)
#out = x.run_kuramoto(scaling_factor = 0.1)
#for track in out.tracks:
#    for msg in track:
#        Out_MIDI_data.write("{0}\n".format(msg))
#
#
#out.save('Output MIDI.mid')

