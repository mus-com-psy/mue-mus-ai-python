# Copyright Tom Collins, 21.1.2024
# Pre-processing MIDI files, calculating their mean MIDI note number, and
# writing them to file.

# Requires
import numpy as np
import pretty_midi

# Can't be bothered with individual user paths for this example!
midi_file_path = 'short_file.mid'

# Parameters
# ...

# Declare/initialize the variables that will contain the results of the analysis.
my_arr = []
# const myObj = {}

# Load MIDI file
midi_data = pretty_midi.PrettyMIDI(midi_file_path)

# Accessing instruments
for i, instrument in enumerate(midi_data.instruments):
    print(f"Instrument {i} - Program: {instrument.program}, Is Drum: {instrument.is_drum}")

# Accessing notes
for i, instrument in enumerate(midi_data.instruments):
    print(f"Notes for Instrument {i}:")
    for note in instrument.notes:
        print(f"Start: {note.start}, End: {note.end}, Pitch: {note.pitch}, Velocity: {note.velocity}")
        my_arr.append(note.pitch)

# Convert the MIDI note numbers list to a numpy array.
mnn_arr = np.array(my_arr)

# Calculate the mean.
mean_mnn = np.mean(mnn_arr)

# Print the result.
print("Mean MNN:", mean_mnn)
