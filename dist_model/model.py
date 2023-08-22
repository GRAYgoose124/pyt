from tensorflow.keras.layers import (
    Input,
    Dense,
    RNN,
    LSTMCell,
    concatenate,
    Bidirectional,
    LSTM,
    Dot,
    Activation,
    Flatten,
    Add,
    Lambda,
    Conv1D,
    MaxPooling1D,
    GlobalMaxPooling1D,
)
from tensorflow.keras.models import Model

MAX_STRING_LENGTH = 100  # Just a placeholder; set it to your value
CHAR_DICT_SIZE = 26  # Assuming only lowercase alphabets; change accordingly


def create_model():
    # Base Network
    def create_base_network():
        input_seq = Input(shape=(MAX_STRING_LENGTH, CHAR_DICT_SIZE))

        # Bidirectional LSTM
        bi_lstm = Bidirectional(LSTM(128, return_sequences=True))(input_seq)

        # CNN layers
        conv1 = Conv1D(filters=64, kernel_size=3, activation="relu")(bi_lstm)
        pool1 = MaxPooling1D(pool_size=2)(conv1)
        conv2 = Conv1D(filters=128, kernel_size=3, activation="relu")(pool1)
        pool2 = MaxPooling1D(pool_size=2)(conv2)
        flat = GlobalMaxPooling1D()(pool2)

        return Model(inputs=input_seq, outputs=flat)

    base_network = create_base_network()

    input_string1 = Input(shape=(MAX_STRING_LENGTH, CHAR_DICT_SIZE))
    input_string2 = Input(shape=(MAX_STRING_LENGTH, CHAR_DICT_SIZE))

    encoded_string1 = base_network(input_string1)
    encoded_string2 = base_network(input_string2)

    # Combine and process the features from both strings
    merged = concatenate([encoded_string1, encoded_string2])

    # Dense layers
    dense1 = Dense(256, activation="relu")(merged)
    dense2 = Dense(128, activation="relu")(dense1)
    dense3 = Dense(64, activation="relu")(dense2)

    output = Dense(1, activation="relu")(dense3)

    model = Model(inputs=[input_string1, input_string2], outputs=output)
    model.compile(optimizer="adam", loss="mse")

    return model
