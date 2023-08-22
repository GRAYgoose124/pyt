# this model requires tensorflow - you're on your own for that one
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, RNN, LSTMCell, concatenate
from tensorflow.keras.models import Model

from pyt.editslist import Edit, EditsList


MAX_STRING_LENGTH = 100  # Just a placeholder; set it to your value
CHAR_DICT_SIZE = 26  # Assuming only lowercase alphabets; change accordingly


def create_model():
    # Input tensors for the two strings
    input_string1 = Input(shape=(MAX_STRING_LENGTH, CHAR_DICT_SIZE))
    input_string2 = Input(shape=(MAX_STRING_LENGTH, CHAR_DICT_SIZE))

    # RNN layer with LSTMCell to get a fixed size encoding for each string
    lstm_cell = LSTMCell(128)
    rnn_layer = RNN(lstm_cell)

    encoded_string1 = rnn_layer(input_string1)
    encoded_string2 = rnn_layer(input_string2)

    # Concatenate the two encoded strings
    merged = concatenate([encoded_string1, encoded_string2])

    # Some dense layers to process the information
    dense1 = Dense(128, activation="relu")(merged)
    dense2 = Dense(64, activation="relu")(dense1)
    dense3 = Dense(32, activation="relu")(dense2)

    # Output layer: predict the Levenshtein distance (scalar value)
    output = Dense(1, activation="relu")(
        dense3
    )  # We use relu because distances can't be negative

    model = Model(inputs=[input_string1, input_string2], outputs=output)
    model.compile(
        optimizer="adam", loss="mse"
    )  # We'll use mean squared error as the loss function

    return model


# if exists load model instead
if os.path.exists("levendist.keras"):
    print("LOADED")
    model = tf.keras.models.load_model("levendist.keras")
else:
    model = create_model()
model.summary()


# TODO: You'd need to preprocess your strings into the required one-hot encoded format and then
# use model.fit() to train the model on pairs of strings and their corresponding Levenshtein distances.
def preprocess_string(s):
    # Convert the string to a list of indices based on the character's position in the alphabet
    # 'a' -> 0, 'b' -> 1, ..., 'z' -> 25
    indices = [ord(c) - ord("a") for c in s]

    # Create a one-hot encoded matrix of shape (MAX_STRING_LENGTH, CHAR_DICT_SIZE)
    one_hot_matrix = np.zeros((MAX_STRING_LENGTH, CHAR_DICT_SIZE))
    for i, index in enumerate(indices):
        one_hot_matrix[i, index] = 1

    return one_hot_matrix


# we can use s1, s2, EditsList.compute(s1, s2) to create a dataset to fit
import random

# List of words to use for generating the dataset
with open("wordlist.10000", "r") as file:
    words = file.read().splitlines()[:250]

# Generate a dataset of pairs of words and their corresponding Levenshtein distances
dataset = []
for i in range(len(words)):
    for j in range(i + 1, len(words)):
        s1 = words[i]
        s2 = words[j]
        edits_list = EditsList.compute(s1, s2)
        distance = edits_list.distance
        dataset.append((s1, s2, distance))

# Shuffle the dataset
random.shuffle(dataset)

# Split the dataset into training and testing sets
train_size = int(0.8 * len(dataset))
train_dataset = dataset[:train_size]
test_dataset = dataset[train_size:]

# Preprocess the strings and create the one-hot encoded matrices
x1_train = np.array([preprocess_string(s1) for s1, s2, distance in train_dataset])
x2_train = np.array([preprocess_string(s2) for s1, s2, distance in train_dataset])
y_train = np.array([distance for s1, s2, distance in train_dataset])

x1_test = np.array([preprocess_string(s1) for s1, s2, distance in test_dataset])
x2_test = np.array([preprocess_string(s2) for s1, s2, distance in test_dataset])
y_test = np.array([distance for s1, s2, distance in test_dataset])

print(dataset)

# Fit the model on the training dataset
model.fit([x1_train, x2_train], y_train, epochs=250, batch_size=64)

# Evaluate the model on the testing dataset
loss = model.evaluate([x1_test, x2_test], y_test)
print("Test loss:", loss)

# Predict the Levenshtein distance between two strings
avg_error = 0
for s1, s2, distance in dataset[-10:]:
    error = (
        model.predict(
            [
                np.array([preprocess_string(s1)]),
                np.array([preprocess_string(s2)]),
            ]
        )[0][0]
        - distance
    )
    print(error)
    avg_error += abs(error)
avg_error /= 10
print("Average error:", avg_error)

# Save the model
model.save("levendist.keras")
