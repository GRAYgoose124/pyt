from editslist import Edit, EditsList
import numpy as np
import itertools
from pathlib import Path
from datasets import Dataset


MAX_STRING_LENGTH = 100


def preprocess_string(s):
    # Return the indices as-is without one-hot encoding
    indices = np.array([ord(c) - ord("a") for c in s])
    padded = np.zeros(MAX_STRING_LENGTH)
    padded[: len(indices)] = indices
    return padded.reshape(-1, 1)


# we can use s1, s2, EditsList.compute(s1, s2) to create a dataset to fit

# List of words to use for generating the dataset
with Path("../data/wordlist.10000").open("r") as file:
    words = file.read().splitlines()


# Generate a dataset of pairs of words and their corresponding Levenshtein distances
dataset = []
for s1, s2 in itertools.combinations(words, 2):
    dataset.append(
        {
            "string1": preprocess_string(s1),
            "string2": preprocess_string(s2),
            "distance": EditsList.compute(s1, s2).distance,
        }
    )
    if len(dataset) % 100000 == 0:
        print(len(dataset))

    if len(dataset) >= 1000000:
        break

# Convert it to a Hugging Face Dataset
hf_dataset = Dataset.from_dict(
    {
        "string1": [x["string1"] for x in dataset],
        "string2": [x["string2"] for x in dataset],
        "distance": [x["distance"] for x in dataset],
    }
)

# Save the dataset to disk for usave with load_dataset()
# cannot use Dataset.save_to_disk as it laods a DatasetDict
hf_dataset.save_to_disk("../data/ldist_wordlist")
