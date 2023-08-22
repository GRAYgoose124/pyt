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
from utils import preprocess_string


def main():
    # setup dataset

    # Fit the model on the training dataset
    MODEL_FILE = str(Path(__file__).parent.parent / "data/levendist.keras")
    while True:
        tf.keras.backend.clear_session()

        if os.path.exists(MODEL_FILE):
            model = tf.keras.models.load_model(MODEL_FILE)
            print("\n\nMODEL LOADED FROM CHECKPOINT\n\n")

        else:
            model = create_model()
            model.summary()

        try:
            model.fit([x1_train, x2_train], y_train, epochs=250, batch_size=32)
        except KeyboardInterrupt:
            break
        finally:
            model.save(MODEL_FILE)

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
        print(error + distance, distance, s1, s2)
        avg_error += abs(error)
    avg_error /= 10
    print("Average error:", avg_error)


if __name__ == "__main__":
    main()
