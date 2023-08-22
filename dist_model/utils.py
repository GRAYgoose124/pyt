import numpy as np


def preprocess_string(s):
    # Convert the string to a list of indices based on the character's position in the alphabet
    # 'a' -> 0, 'b' -> 1, ..., 'z' -> 25
    indices = [ord(c) - ord("a") for c in s]

    # Create a one-hot encoded matrix of shape (MAX_STRING_LENGTH, CHAR_DICT_SIZE)
    one_hot_matrix = np.zeros((MAX_STRING_LENGTH, CHAR_DICT_SIZE))
    for i, index in enumerate(indices):
        one_hot_matrix[i, index] = 1

    return one_hot_matrix
