# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 14:08:15 2018

@author: Chris
"""

import mido
import math

def get_tempo_and_frequency(tracks):
    for msg in tracks:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            frequency = mido.tempo2bpm(msg.tempo)/60
    return tempo, frequency


def get_MIDI_phases_and_times(MIDI_File, tempo, frequency):
    midi_phases = []
    midi_times = []
    for track in MIDI_File.tracks:
        phases = []
        times = []
        phase = 0
        time = 0
        for msg in track:       
            #MIDI_data.write("{0} \n".format(msg))   
            if msg.type == 'note_on':
                phase += 2*math.pi*frequency*mido.tick2second(msg.time, MIDI_File.ticks_per_beat, tempo)
                time += mido.tick2second(msg.time, MIDI_File.ticks_per_beat, tempo)
                times.append(time)
                phases.append(math.ceil(phase*100)/100)
    
        midi_phases.append(phases)
        midi_times.append(times)
    return midi_phases, midi_times


def check(midi_phase, osc_phase):
    if midi_phase-0.001 <= osc_phase <= midi_phase+0.001:
        return True
    return False

def compute_output_kuramoto_phases(input_midi_phases, kuramoto_phases, frequency, instant_freqs):
    
    output_midi_phases = []
    output_midi_instant_freq = []
    added = False
    i = 0
    temp = 0
    
    for track in input_midi_phases:
        output_midi_phase = []
        output_midi_instant_track_freq = []
        note_number = 0
        for midi_phase in track:
            j = 0
            for osc_phase in kuramoto_phases[i]:
                if check(midi_phase, osc_phase) and added == False:
                    #output.write("Channel: {0} Note Number: {1} MIDI phase: {2} OSC_phase: {3}\n".format(i, note_number, midi_phase, osc_phase))
                    output_midi_phase.append(osc_phase)
                    output_midi_instant_track_freq.append(instant_freqs[i][j-1])
                    temp = instant_freqs[i][j]
                    added = True
                    break
                j+=1
        
            if added == False:
                output_midi_phase.append(midi_phase)
                output_midi_instant_track_freq.append(temp)
                #output.write("Channel: {0} MIDI note {1} not added. MIDI phase: {2}\n".format(i, note_number, midi_phase))
                
            note_number += 1
            added = False        
        output_midi_phases.append(output_midi_phase)
        output_midi_instant_freq.append(output_midi_instant_track_freq)
        i += 1
    
    return output_midi_phases, output_midi_instant_freq

def compute_output_kuramoto_times(output_midi_phases, instant_freqs):
    output_midi_times = []
    i=0
    for track in output_midi_phases:
        output_midi_track_times = []
        j=0
        for phase in track:
            output_midi_track_times.append(phase/(instant_freqs[i][j-1]))
            j+=1
        i+=1
        output_midi_times.append(output_midi_track_times)
    return output_midi_times