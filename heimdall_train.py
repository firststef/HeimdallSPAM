import os
import pickle
import random
import string
import nltk

from nltk.classify import MaxentClassifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

from heimdall_utils import decode_mail

eng_words = None
def process_text(text):
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Convert to lowercase
    text = text.lower()

    # Tokenize words
    words = word_tokenize(text)

    # Remove stop words
    global eng_words
    if eng_words == None:
        eng_words = stopwords.words("english")
    words = [word for word in words if word not in eng_words]

    return words

def get_features(text, feature_list):
    words = process_text(text)
    features = {}
    for word in feature_list:
        features[word] = (word in words)
    return features

def train_nltk(data):
    nltk.download('punkt')
    nltk.download('stopwords')

    spam_messages = []
    ham_messages = []

    for content, type in data:
        if type == 'inf':
            spam_messages.append(content)
        if type == 'cln':
            ham_messages.append(content)

    all_words = []
    for message in spam_messages:
        all_words += process_text(message)
    for message in ham_messages:
        all_words += process_text(message)

    # Get the most common words
    word_freq = nltk.FreqDist(all_words)
    common_words = list(word_freq.keys())[:100]

    # Create feature sets
    spam_features = [(get_features(message, common_words), "inf") for message in spam_messages]
    ham_features = [(get_features(message, common_words), "cln") for message in ham_messages]

    # Split the feature sets into training and testing sets
    random.shuffle(spam_features)
    random.shuffle(ham_features)
    spam_train_size = int(len(spam_features) * 0.8)
    ham_train_size = int(len(ham_features) * 0.8)
    spam_train_set = spam_features[:spam_train_size]
    spam_test_set = spam_features[spam_train_size:]
    ham_train_set = ham_features[:ham_train_size]
    ham_test_set = ham_features[ham_train_size:]

    # Train the classifier
    classifier = MaxentClassifier.train(spam_train_set + ham_train_set)

    # Print the accuracy of the classifier
    print(nltk.classify.accuracy(classifier, spam_test_set + ham_test_set))

    with open("heimdall_train3.sav", "wb") as f:
        pickle.dump([classifier, common_words], f)

serialized_classif = None
def heimdall_classify(content):
    global serialized_classif
    if serialized_classif == None:
        with open("heimdall_train3.sav", "rb") as f:
            serialized_classif = pickle.load(f)
    classifier, common_words = serialized_classif

    res = classifier.classify(get_features(content, common_words))
    return res == 'inf'

def train_sci(data):
    inputs = []
    labels = []
    for content, type in data:
        inputs.append(content)
        labels.append(type)

    tfidfvectorizer = TfidfVectorizer(stop_words="english", strip_accents="ascii", token_pattern=r"(?u)\b[A-Za-z]+\b")
    inputs = tfidfvectorizer.fit_transform(inputs).toarray()

    classifier = RandomForestClassifier()
    classifier.fit(inputs, labels)

    with open("heimdall_train4.sav", "wb") as f:
        pickle.dump([classifier, tfidfvectorizer], f)

serialized_decide = None
def heimdall_decide(content):
    global serialized_decide
    if serialized_decide == None:
        with open("heimdall_train4.sav", "rb") as f:
            serialized_decide = pickle.load(f)
    classifier, vectorizer = serialized_decide

    converted = vectorizer.transform([content])
    verdicts = classifier.predict(converted)
    return verdicts[0] == 'inf'

def heimdall_decide_multi(contents):
    global serialized_decide
    if serialized_decide == None:
        with open("heimdall_train4.sav", "rb") as f:
            serialized_decide = pickle.load(f)
    classifier, vectorizer = serialized_decide

    converted = vectorizer.transform(contents)
    verdicts = classifier.predict(converted)
    return verdicts

def heimdall_train(test_fixtures):
    data = []
    for dir, status in test_fixtures.items():
        for filename in os.listdir(dir):
            with open(os.path.join(dir, filename), "r", errors="ignore") as f:
                content = f.read()
                content = decode_mail(content) # base64 decode
                data.append((content, status))
    # train_nltk(data)
    train_sci(data)
