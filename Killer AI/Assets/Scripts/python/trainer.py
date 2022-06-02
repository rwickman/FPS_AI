import torch
import torch.nn as nn
import torch.optim as optim
import json, os

from replay_dataset import get_dataloader
from config import *


class ImitationTrainer:
    def __init__(self, policy):
        self.policy = policy
        self.loss_fn = nn.CrossEntropyLoss()


        self.train_dataloader, self.val_dataloader = get_dataloader()
        self.train_dict = {"train_loss": [], "val_loss": []}
        self.train_dict_file = os.path.join(save_dir, "train_dict.json")

        if load:
            self.load()

    def save(self):
        self.policy.save()
        # Save the training results
        with open(self.train_dict_file, "w") as f:
            json.dump(self.train_dict, f)
        
        print("SAVED CHECKPOINT")

    def load(self):
        self.policy.load()
        with open(self.train_dict_file) as f:
            self.train_dict = json.load(f)

    def validate(self):
        print("VALIDATING")
        self.policy.model.eval()
        for actions, states, masks in self.val_dataloader:
            preds = self.policy.predict(states, masks)
            val_loss = 0

            for i in range(len(preds)):
                val_loss += self.loss_fn(preds[i], actions[:, i])
                # print(preds[i])
                # print(actions[:, i])
            self.train_dict["val_loss"].append(val_loss.item())



        self.policy.model.train()
        print("DONE VALIDATING")


    def train(self):
        cur_iter = 0
        for epoch in range(epochs):
            print("TRAINING ON EPOCH: ", epoch)
            for actions, states, masks in self.train_dataloader:
                self.policy.optimizer.zero_grad()
                preds = self.policy.predict(states, masks)
                loss = 0

                for i in range(len(preds)):
                    loss += self.loss_fn(preds[i], actions[:, i])
                loss.backward()
                self.policy.optimizer.step()
                self.train_dict["train_loss"].append(loss.item())
                cur_iter += 1
                #if cur_iter % 256 == 0:
            self.save()
            
            self.validate()
        
        self.save()
