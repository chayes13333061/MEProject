# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 18:57:11 2018

@author: Chris
"""

from Kuramoto_with_MIDI import Kuramoto_with_MIDI
from mido import Message, MidiFile, MidiTrack, MetaMessage, frozen

mid = MidiFile('AC_DC_-_Back_In_Black.mid')

MIDI_data = open('MIDI_data.txt', 'w')
Out_MIDI_data = open('Out_MIDI_data.txt', 'w')

for track in mid.tracks:
    for msg in track:
        MIDI_data.write("{0}\n".format(msg))

x = Kuramoto_with_MIDI(mid)
out = x.run_kuramoto(scaling_factor = 0.02)
for track in out.tracks:
    for msg in track:
        Out_MIDI_data.write("{0}\n".format(msg))


out.save('Output MIDI.mid')