import sys
import re
import os
import time
import pickle as pkl
from datetime import timedelta
from tqdm import tqdm

import numpy as np
import torch 
import torch.nn as nn
import torch.nn.functional as F
from sklearn import metrics
from pytorch_pretrained_bert import BertModel, BertTokenizer
from pytorch_pretrained_bert.optimization import BertAdam
from __utils.__path_util import global_path

class Config:
    """Configuration for the Model"""
    def __init__(self, dataset_name):
        self.model_name = "bertrnn"
        self.dataset_name = dataset_name

        # Dataset paths
        self.train_path = global_path.__dataset_path__ + '/train.txt'
        self.dev_path = global_path.__dataset_path__ + '/valid.txt'
        self.test_path = global_path.__dataset_path__ + '/test.txt'
        self.dataset_pkl = f'./pkl/{dataset_name}.pkl'

        # Model paths
        self.bert_path = './bert-base-uncased'
        self.save_path = f'./ckpt/{dataset_name}.ckpt'

        # Tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)

        # Training parameters
        self.device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
        self.num_epochs = 50
        self.batch_size = 64
        self.pad_size = 73
        self.learning_rate = 1e-5
        self.require_improvement = 1000  # Early stopping

        # Label and class info
        self.num_classes = 379
        self.class_list = [str(i) for i in range(self.num_classes)]

        # Model hyperparameters
        self.hidden_size = 768
        self.dropout = 0.1


class DatasetManager:
    """Handles Dataset Loading, Preprocessing, and Iterators"""
    PAD, CLS = '[PAD]', '[CLS]'

    def __init__(self, config):
        self.config = config

    def preprocess_text(self, text):
        """Text preprocessing."""
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[-—'\"]", " ", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def load_dataset(self, file_path):
        """Load dataset and tokenize."""
        contents = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f):
                line = line.strip()
                if not line:
                    continue
                content, label = line.split('\t')
                content = self.preprocess_text(content)
                token = self.config.tokenizer.tokenize(content)
                token = [self.CLS] + token
                seq_len = len(token)
                token_ids = self.config.tokenizer.convert_tokens_to_ids(token)
                mask = [1] * len(token_ids) + [0] * (self.config.pad_size - len(token_ids))
                token_ids += [0] * (self.config.pad_size - len(token_ids))
                seq_len = min(seq_len, self.config.pad_size)
                contents.append((token_ids, int(label), seq_len, mask))
        return contents

    def build_dataset(self):
        """Build dataset and cache."""
        if os.path.exists(self.config.dataset_pkl):
            with open(self.config.dataset_pkl, 'rb') as f:
                dataset = pkl.load(f)
        else:
            train = self.load_dataset(self.config.train_path)
            dev = self.load_dataset(self.config.dev_path)
            dataset = {"train": train, "dev": dev}
            with open(self.config.dataset_pkl, 'wb') as f:
                pkl.dump(dataset, f)
        return dataset["train"], dataset["dev"]

    class DatasetIterator:
        """Custom Iterator for Datasets"""
        def __init__(self, dataset, batch_size, device):
            self.dataset = dataset
            self.batch_size = batch_size
            self.device = device
            self.n_batch = len(dataset) // batch_size
            self.residue = len(dataset) % batch_size != 0
            self.index = 0

        def _to_tensor(self, data):
            x = torch.LongTensor([item[0] for item in data]).to(self.device)
            y = torch.LongTensor([item[1] for item in data]).to(self.device)
            seq_len = torch.LongTensor([item[2] for item in data]).to(self.device)
            mask = torch.LongTensor([item[3] for item in data]).to(self.device)
            return (x, seq_len, mask), y

        def __next__(self):
            if self.index >= self.n_batch + int(self.residue):
                self.index = 0
                raise StopIteration
            batch = self.dataset[self.index * self.batch_size:(self.index + 1) * self.batch_size]
            self.index += 1
            return self._to_tensor(batch)

        def __iter__(self):
            return self

    def build_iterator(self, dataset):
        return self.DatasetIterator(dataset, self.config.batch_size, self.config.device)


class BertClassifier(nn.Module):
    """BERT-based Classification Model"""
    def __init__(self, config):
        super(BertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(config.bert_path)
        self.fc = nn.Linear(config.hidden_size, config.num_classes)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        context, seq_len, mask = x
        _, pooled = self.bert(context, attention_mask=mask, output_all_encoded_layers=False)
        output = self.dropout(self.fc(pooled))
        return output


class Trainer:
    """Handles Training and Evaluation"""
    def __init__(self, config, model, dataset_manager):
        self.config = config
        self.model = model.to(config.device)
        self.dataset_manager = dataset_manager

    def train(self, train_iter, dev_iter):
        optimizer = BertAdam(params=self.model.parameters(), lr=self.config.learning_rate, warmup=0.05)
        best_acc = 0
        total_batch = 0

        for epoch in range(self.config.num_epochs):
            print(f"Epoch {epoch + 1}/{self.config.num_epochs}")
            self.model.train()
            for i, (trains, labels) in enumerate(train_iter):
                outputs = self.model(trains)
                loss = F.cross_entropy(outputs, labels)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if total_batch % 5 == 0:
                    acc = self.evaluate(dev_iter)
                    if acc > best_acc:
                        best_acc = acc
                        torch.save(self.model.state_dict(), self.config.save_path)
                    print(f"Iter {total_batch}, Loss: {loss.item():.4f}, Val Acc: {acc:.4f}")
                total_batch += 1
        print(f"Training complete. Best Accuracy: {best_acc:.4f}")

    def evaluate(self, data_iter):
        self.model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for texts, labels in data_iter:
                outputs = self.model(texts)
                all_preds.extend(torch.max(outputs, 1)[1].cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        return metrics.accuracy_score(all_labels, all_preds)


if __name__ == "__main__":
    config = Config("dataset")
    dataset_manager = DatasetManager(config)

    train_data, dev_data = dataset_manager.build_dataset()
    train_iter = dataset_manager.build_iterator(train_data)
    dev_iter = dataset_manager.build_iterator(dev_data)

    model = BertClassifier(config)
    trainer = Trainer(config, model, dataset_manager)

    trainer.train(train_iter, dev_iter)
