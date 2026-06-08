from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

train_texts = [
    "murder attack kill death threat shoot bomb explosion",
    "rape sexual assault kidnap abduct hostage",
    "armed robbery weapon gun knife violent attack",
    "emergency urgent critical immediate danger life threat",
    "fraud cheating scam stolen money bank deceive",
    "hacking cyber attack online theft data breach",
    "accident injury hospital hurt wound",
    "property dispute land encroachment illegal",
    "noise complaint minor issue small problem",
    "information request general query document",
    "corruption bribe government officer illegal money",
    "domestic violence abuse harassment family",
]

train_labels = [
    "Urgent", "Urgent", "Urgent", "Urgent",
    "High", "High", "High", "High",
    "Normal", "Normal", "High", "Urgent",
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(train_texts)
model = MultinomialNB()
model.fit(X, train_labels)

def suggest_priority(description):
    X_test = vectorizer.transform([description.lower()])
    priority = model.predict(X_test)[0]
    return priority