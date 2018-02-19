README

Requires the mido library https://github.com/olemb/mido/tree/stable. 

This program reads in a MIDI file as input and then outputs a similar MIDI file with timing deviations. The timing 
deviations are added by treating each track in the MIDI file as an oscillator with a certain frequency and phase. Each 
oscillator is coupled with every other oscillator via a coupling constant, which can be manually set in the program as
an input to the program. 

The frequency synchronisation between the oscillators is described via the Kuramoto model, which describes a network of
coupled oscillators settling on a single global frequency. The synchronisation between each oscillator gives rise to 
slight perturbations in the instantaneous frequencies of each oscillator and in turn causes slight timing differences
between each oscillator. 

These slight timing differences have been shown to give music a sense of groove, and such is the nature of this project. 

PROGRAM
This program takes any MIDI file as input and produces a MIDI file with timing deviations depending on particular parameters
set by the user. The midi message defining the tempo of the song should be in the first track in the MIDI file to work 
correctly. 

The run_kuramoto() function can take three arguments: 

1) Coupling constants between each instrument in an MIDI file to be used in solving the ordinary differential equations of 
the kuramoto model. Default: 25x25 matrix containing just ones

2) Coupling constant between each instrument in an MIDI file to be used in solving the Jacobian of the ordinary differential equations of 
the kuramoto model. Default 25x25 matrix containing just ones

3) Scaling factor, this scales the coupling constant by a number chosen by the user. Default: scaling_factor = 1

Plots/ diagrams need to be added and improved.