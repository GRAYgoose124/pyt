from pyt.editslist import Edit, EditsList

# we can use s1, s2, EditsList.compute(s1, s2) to create a dataset to fit

# List of words to use for generating the dataset
with open("wordlist.10000", "r") as file:
    _words = file.read().splitlines()
    # take 500 random lines
    words = random.sample(_words, 250)
    _words2 = random.sample(_words, 250)
    words += [w1 + w2 for w1, w2 in zip(words, _words2)]


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
