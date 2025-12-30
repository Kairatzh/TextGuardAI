import pandas as pd 
from configs.config import load_configs

configs = load_configs()

train_data = pd.read_csv(configs["data"]["train_data"])
test_data = pd.read_csv(configs["data"]["test_data"])

print(train_data.head())
print(test_data.head())

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stopwords = nltk.corpus.stopwords.words("english")
lemmatizer = nltk.WordNetLemmatizer()
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')

class TextPreprocessor:
    def __init__(self):
        self.stopwords = stopwords
        self.lemmatizer = lemmatizer
        self.tokenizer = tokenizer
    
    def preprocess(self, text):
        text = text.lower()
        tokens = self.tokenizer.tokenize(text)
        tokens = [word for word in tokens if word not in self.stopwords]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return " ".join(tokens)

preprocessor = TextPreprocessor()
train_data["comment_text"] = train_data["comment_text"].apply(preprocessor.preprocess)
test_data["comment_text"] = test_data["comment_text"].apply(preprocessor.preprocess)

print(train_data.head())
print(test_data.head())

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
train_texts = vectorizer.fit_transform(train_data["comment_text"]).toarray()
test_texts = vectorizer.transform(test_data["comment_text"]).toarray()

train_labels = train_data["toxic"].tolist()
test_labels = test_data["toxic"].tolist()

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from torch.nn import Linear, Dropout, ReLU, Module

class CustomTextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = torch.tensor(texts, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, index):
        return self.texts[index], self.labels[index]

train_dataset = CustomTextDataset(train_texts, train_labels)
test_dataset = CustomTextDataset(test_texts, test_labels)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

input_size = train_texts.shape[1]

class TextClassifier(Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(TextClassifier, self).__init__()
        self.fc1 = Linear(input_size, hidden_size)
        self.fc2 = Linear(hidden_size, output_size)
        self.relu = ReLU()
        self.dropout = Dropout(0.5)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

model = TextClassifier(input_size=input_size, hidden_size=128, output_size=2)
optimizer = AdamW(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

train_losses = []
test_losses = []
train_accuracies = []
test_accuracies = []

epochs = 10
for epoch in range(epochs):
    model.train()
    train_loss = 0.0
    train_correct = 0
    train_total = 0
    for texts, labels in train_loader:
        texts = texts.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        outputs = model(texts)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        train_correct += (outputs.argmax(dim=1) == labels).sum().item()
        train_total += labels.size(0)
    train_loss /= len(train_loader)
    train_accuracy = train_correct / train_total
    train_losses.append(train_loss)
    train_accuracies.append(train_accuracy)
    
    model.eval()
    test_loss = 0.0
    test_correct = 0
    test_total = 0
    with torch.no_grad():
        for texts, labels in test_loader:
            texts = texts.to(device)
            labels = labels.to(device)
            outputs = model(texts)
            loss = criterion(outputs, labels)
            test_loss += loss.item()
            test_correct += (outputs.argmax(dim=1) == labels).sum().item()
            test_total += labels.size(0)
    test_loss /= len(test_loader)
    test_accuracy = test_correct / test_total
    test_losses.append(test_loss)
    test_accuracies.append(test_accuracy)
    print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")

print(train_losses)
print(train_accuracies)
print(test_losses)
print(test_accuracies)