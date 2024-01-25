import pretty_midi

midi_file_path = 'short_file.mid'

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
