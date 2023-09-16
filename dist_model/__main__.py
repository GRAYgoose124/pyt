# this model requires tensorflow - you're on your own for that one
import os
import numpy as np
import random
import tensorflow as tf

# from tensorflow.keras.layers import (
#     Input,
#     Dense,
#     RNN,
#     LSTMCell,
#     concatenate,
#     Bidirectional,
#     LSTM,
#     Dot,
#     Activation,
#     Flatten,
#     Add,
#     Lambda,
#     Conv1D,
#     MaxPooling1D,
#     GlobalMaxPooling1D,
# )
from pathlib import Path

from model import create_model

from datasets import load_from_disk


def preprocess_string(s):
    # Return the indices as-is without one-hot encoding
    indices = np.array([ord(c) - ord("a") for c in s])
    padded = np.zeros(
        100
    )  # MAX_STRING_LENGTH - tbh need to make dist_model a proper package or something idk
    padded[: len(indices)] = indices
    return padded.reshape(-1, 1)


def main():
    root = Path(__file__).parent
    MODEL_FILE = root / "data/levendist.keras"

    if input("Want to train? (y/n) ").lower() == "y":
        # setup dataset
        dataset = load_from_disk(root / "data/ldist_wordlist")
        dataset = dataset.shuffle()
        dataset = dataset.train_test_split(test_size=0.1)
        dataset = dataset.with_format("tf")
        # only use the first 1000 examples for now
        dataset["train"] = dataset["train"].select(range(1000))
        dataset["test"] = dataset["test"].select(range(1000))

        x_train = dataset["train"]["string1"]
        x2_train = dataset["train"]["string2"]
        y_train = dataset["train"]["distance"]

        x_test = dataset["test"]["string1"]
        x2_test = dataset["test"]["string2"]

        # Fit the model on the training dataset
        while True:
            tf.keras.backend.clear_session()

            if os.path.exists(MODEL_FILE):
                model = tf.keras.models.load_model(MODEL_FILE)
                print("\n\nMODEL LOADED FROM CHECKPOINT\n\n")
            else:
                model = create_model()
                model.summary()

            try:
                model.fit(
                    [x_train, x2_train],
                    y_train,
                    epochs=256,
                    batch_size=32,
                )
            except KeyboardInterrupt:
                break
            finally:
                model.save(MODEL_FILE)

        # Evaluate the model on the testing dataset
        loss = model.evaluate(
            [x_test, x2_test],
        )
        print("Test loss:", loss)
    else:
        if not os.path.exists(MODEL_FILE):
            print("No model found. Please train first.")
            return
        model = tf.keras.models.load_model(MODEL_FILE)

    # Predict the Levenshtein distance between a few words
    while True:
        user_input = input("Enter two words separated by a space: ")
        if user_input == "exit":
            break

        w1, w2 = user_input.split(" ")
        # w1, w2 = preprocess_string(w1), preprocess_string(w2)
        w1_processed = preprocess_string(w1).reshape(
            1, 100, 1
        )  # Adding batch dimension
        w2_processed = preprocess_string(w2).reshape(
            1, 100, 1
        )  # Adding batch dimension

        ev = model.evaluate([w1_processed, w2_processed])
        print("Predicted Levenshtein distance:", ev)


if __name__ == "__main__":
    main()
