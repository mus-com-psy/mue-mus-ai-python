# Some code from ChatGPT's Python LLM for training a transformer neural network architecture to predict the velocity of the next note. With substantial editing and correction by Chenyu Gao and Tom Collins.


# 1. Requirements/dependencies
import mido
import os
import numpy as np
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
import tqdm


# 0. Helper functions/classes
def split_midi_files(directory_path, test_size, val_size, random_seed):
    """
    Splits the MIDI files in a directory into training, validation, and test sets.

    The files are split so that no tokens from the same MIDI file appear in more than one set.
    """
    # Get all the MIDI files in the directory
    midi_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.mid')]

    # Split into train+val and test sets
    train_val_files, test_files = train_test_split(midi_files, test_size=test_size, random_state=random_seed)

    # Further split the train+val set into train and validation sets
    train_files, val_files = train_test_split(train_val_files, test_size=val_size / (1 - test_size), random_state=random_seed)

    return train_files, val_files, test_files

def tokenize_midi_files(file_paths):
    """Tokenize all MIDI files from a given list of file paths and combine their tokens."""
    all_tokens = []

    for file_path in file_paths:
        print(f"Processing {file_path}...")

        # Try to parse and tokenize the MIDI file
        try:
            tokens = parse_midi(file_path)

            # Add the tokens from this file to the total token list
            all_tokens.extend(tokens)

        except( OSError, ValueError) as e:
            # Catching common file-related errors or parsing errors
            print(f"Skipping {file_path} due to an error: {str(e)}")

    return all_tokens

def parse_midi(file_path):
    """Parse a single MIDI file and extract tokenized representation."""
    try:
        midi = mido.MidiFile(file_path)
        tokens = []
        last_tick = 0

        for msg in midi:
            if msg.type in ['note_on', 'note_off']:
                tick_diff = msg.time - last_tick
                last_tick = msg.time

                # Tokenize (tick_diff, note, velocity)
                if msg.type == 'note_on' and msg.velocity > 0:
                    tokens.append((tick_diff, msg.note, msg.velocity))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Tokenize note off event with velocity 0
                    tokens.append((tick_diff, msg.note, 0))

        return tokens

    except (OSError, ValueError) as e:
        # Catching common file-related errors or parsing errors
        print(f"Skipping {file_path} due to an error: {str(e)}")

        return

def prepare_dataset(tokenized_sequences, sequence_length):
    """
    Prepares the dataset by splitting into sequences of a fixed length.
    Each sequence will be used to predict the velocity of the next note.
    """
    X, y = [], []
    for i in range(len(tokenized_sequences) - (sequence_length + 1)):
        # Extract the sequence
        sequence = tokenized_sequences[i:i + sequence_length]

        # The next token's velocity will be the target
        next_velocity = tokenized_sequences[i + sequence_length + 1][2]

        # Append the sequence and the target velocity
        X.append(sequence)
        y.append(next_velocity)

    return np.array(X), np.array(y)

# PyTorch transformer model
class MidiTransformer(nn.Module):
    def __init__(self, input_dim, model_dim, num_heads, num_layers, output_dim, dropout=0.1):
        super(MidiTransformer, self).__init__()
        self.embeddingSrc = nn.Linear(input_dim, model_dim)
        self.embeddingTgt = nn.Linear(output_dim, model_dim)
        self.transformer = nn.Transformer(
            d_model=model_dim,
            nhead=num_heads,
            num_encoder_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        self.fc = nn.Linear(model_dim, output_dim)

    def forward(self, src, tgt):
        # Embed the input tokens [batch_size, seq_len, (tick, note, velocity)]
        # import pdb; pdb.set_trace()
        src = self.embeddingSrc(src)

        # Embed the output tokens [batch_size, seq_len, (velocity)]
        # tgt = torch.unsqueeze(tgt, dim=1)
        tgt = torch.unsqueeze(tgt, dim=2)
        # import pdb; pdb.set_trace()
        tgt = self.embeddingTgt(tgt)

        # Chenyu added 'batch_first=True' in line 133, so we don't need to reshape anymore.
        # # Transformer expects shape (sequence_length, batch_size, model_dim)
        # src = src.transpose(0, 1)
        # tgt = tgt.transpose(0, 1)

        # Pass through the transformer
        transformer_out = self.transformer(src, tgt)

        # Take only the last output for prediction
        transformer_out = torch.squeeze(transformer_out)
        output = self.fc(transformer_out)
        return output

def train_model(model, X_train, y_train, X_val, y_val, num_epochs, batch_size, learning_rate):
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    train_data = torch.utils.data.TensorDataset(torch.Tensor(X_train), torch.Tensor(y_train))
    val_data = torch.utils.data.TensorDataset(torch.Tensor(X_val), torch.Tensor(y_val))

    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_data, batch_size=batch_size)

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        print(">>>>>>>Training stage:")
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            targets = torch.unsqueeze(targets, dim=1)
            outputs = model(inputs, targets) # nn.Transformer require both the sequence to the encoder, and that to the decoder as input.
            loss = criterion(outputs, targets)
            print("loss", loss)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        val_loss = 0.0
        model.eval()
        print(">>>>>>>Validation stage:")
        with torch.no_grad():
            for inputs, targets in val_loader:
                outputs = model(inputs, targets)
                loss = criterion(outputs, targets)
                val_loss += loss.item()

        print(f"Epoch {epoch+1}/{num_epochs}, Training Loss: {running_loss/len(train_loader)}, Validation Loss: {val_loss/len(val_loader)}")

def predict_velocity(model, input_sequence):
    model.eval()
    with torch.no_grad():
        input_tensor = torch.Tensor(input_sequence).unsqueeze(0)  # Add batch dimension
        output = model(input_tensor)
        return output.item()


# 2. Define (user-specific) paths
# Example usage:
midi_directory = '/home/txc970/project_files/midis_for_mue_music_ai/hip_hop_mido'
# midi_directory = './dataset/hip_hop_midi/preprocessed'


# 3. Set parameters
sequence_length = 50
test_size = 0.2
val_size = 0.1
random_seed = 42
# Model instantiation
input_dim = 3  # tick_diff, note, velocity
model_dim = 128
num_heads = 4
num_layers = 4
output_dim = 1  # Predicting velocity
# Training parameters
num_epochs = 1
batch_size = 32
learning_rate = 0.001
begin_token = 500


# 4. Declare/initialize output variables
train_files, val_files, test_files = split_midi_files(midi_directory, test_size, val_size, random_seed)
model = MidiTransformer(input_dim, model_dim, num_heads, num_layers, output_dim)

# 5. Iterate to import input files
# 6. Extract features/tokenize
train_tokens = tokenize_midi_files(train_files)
val_tokens = tokenize_midi_files(val_files)
test_tokens = tokenize_midi_files(test_files)
print(f"Training tokens: {len(train_tokens)}, Validation tokens: {len(val_tokens)}, Test tokens: {len(test_tokens)}")

X_train, y_train = prepare_dataset(train_tokens, sequence_length=sequence_length)
X_val, y_val = prepare_dataset(val_tokens, sequence_length=sequence_length)
X_test, y_test = prepare_dataset(test_tokens, sequence_length=sequence_length)

print(f"Training sequences: {X_train.shape}, Validation sequences: {X_val.shape}, Test sequences: {X_test.shape}")

# 7. Train/infer from model
train_model(model, X_train, y_train, X_val, y_val, num_epochs, batch_size, learning_rate)
predicted_velocity = predict_velocity(model, X_test[0])
print(f"Predicted Velocity: {predicted_velocity}")

# 8. Append results to one or more to-be-output variables
# 9. Plot/visualize/sonify results
# 10. Write outputs to file (sometimes after each loop, to avoid exceeding memory limitations)
