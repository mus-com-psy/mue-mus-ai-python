# Copyright Tom Collins, 21.1.2024
# Pre-processing MIDI files, calculating their mean MIDI note number, and
# writing them to file.

# Requires
import os
import getopt, sys
import numpy as np
import matplotlib.pyplot as plt
import pretty_midi

# Individual user paths
mainPaths = {
  "tom": {
    "inDir": os.path.join(
      "/home", "txc970", "project_files", "midis_for_mmi_music_ai", "hip_hop",
      "mid"
    ),
    "outDir": path.join(
      "/home", "txc970", "repos", "mmi-mus-ai-python", "out"
    ),
    "outFileName": "mean_mnns"
  },
  "anotherUser": {
    # ...
  }
}
options = "u:"
longOptions = ["User="]
# in_dir = "/home/txc970/project_files/midis_for_mmi_music_ai/hip_hop_midi/mid"
# out_file_name = "mean_mnns.txt"

# Parameters
# ...

# Declare/initialize the variables that will contain the results of the analysis.
my_arr = []
# const myObj = {}

# Import and analyse the MIDI files.
arguments, values = getopt.getopt(argumentList, options, long_options)
try:
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-u", "--User"):
            print("User!")
            mainPath = mainPaths[currentValue]
except getopt.error as err:
    # output error, and return with an error code
    print(str(err))

files = os.listdir(in_dir)
files = [file for file in files if file.endswith(".mid")]
print("len(files):", len(files))

for file in files:
    midi_file_path = os.path.join(in_dir, file)
    print("file:", file)

    try:
        # Load MIDI file
        midi_data = pretty_midi.PrettyMIDI(midi_file_path)
        all_mnns = []

        # Accessing instruments
        for i, instrument in enumerate(midi_data.instruments):
            print(f"Instrument {i} - Program: {instrument.program}, Is Drum: {instrument.is_drum}")

        # Accessing notes
        for i, instrument in enumerate(midi_data.instruments):
            print(f"Notes for Instrument {i}:")
            for note in instrument.notes:
                # print(f"Start: {note.start}, End: {note.end}, Pitch: {note.pitch}, Velocity: {note.velocity}")
                all_mnns.append(note.pitch)

        # Convert the MIDI note numbers list to a numpy array.
        all_mnns_arr = np.array(all_mnns)
        # Calculate the mean.
        mean_mnn = np.mean(all_mnns_arr)
        # Print the result.
        print("Mean MNN:", mean_mnn)
        my_arr.append(mean_mnn)
    except:
        print("There was an error!")

print("my_arr:", my_arr)
# Histogram plot
# Plotting the histogram
plt.hist(my_arr, bins=20, color="blue", edgecolor="black")

# Adding labels and title
plt.xlabel("Mean MIDI note number")
plt.ylabel("Frequency of observation")
plt.title("Histogram of mean MIDI note numbers")

# Save the plot to a PNG file
plt.savefig("histogram_plot.png")

# Close the plot to free up resources (optional)
plt.close()

with open(out_file_name, "w") as out_file:
    for x in my_arr:
        out_file.write(f"{x}\n")
