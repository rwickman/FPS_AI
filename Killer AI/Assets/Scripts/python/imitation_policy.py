import torch
import torch.nn as nn
import torch.optim as optim

import os
from config import *
from torch.distributions.categorical import Categorical
from replay_dataset import map_state, map_action
from model import ImitationModel
from state_history import StateHistory


class ImitationPolicy:
    def __init__(self, is_training=False):
        self.is_training = is_training
        self.model = self.create_policy()
        self.optimizer = optim.Adam(self.model.parameters(), lr)
        
        # Make the directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        
        self.model_file = os.path.join(save_dir, "il_model.pt")
        
        if not self.is_training:
            self.state_history = StateHistory()

        if load and not self.is_training:
            self.load()
            self.optimizer.param_groups[0]["lr"] = lr
        

    def save(self):
        # Save the model
        model_dict = {
            "model" : self.model.state_dict(),
            "optimizer" : self.optimizer.state_dict()
        }
        torch.save(model_dict, self.model_file)

    def load(self):
        print("LOADING MODEL")
        model_dict = torch.load(self.model_file)
        self.model.load_state_dict(model_dict["model"])
        self.optimizer.load_state_dict(model_dict["optimizer"])

    def create_policy(self):
        model = ImitationModel(not self.is_training).to(device)
        if not self.is_training:
            model.eval()
        return model
    
    def predict(self, state: torch.Tensor, mask: torch.Tensor):
        """Used for training the model."""
        return self.model(state, mask)

    def __call__(self, state_dict: dict, action_vec: list, reward: float) -> int:
        """Used for inference."""
        state, mask = map_state(
            state_dict,
            action_vec,
            reward)

        # Add history to state
        state, mask = self.state_history.update_state(state, mask)
        
        pred_outs = self.model(state.unsqueeze(0), mask.unsqueeze(0))
        #print(len(pred_outs))
        actions = []
        for pred_out in pred_outs:
            actions.append(Categorical(pred_out).sample().item())
        print(len(actions), actions)

        action_dict = {
            "xMouse" : mouse_pos[actions[0]],
            "yMouse" : mouse_pos[actions[1]],
            "xMove" : move_list[actions[2]][0],
            "yMove" : move_list[actions[2]][1],
            "isRunning" : float(actions[3]),
            "isJumping" : float(actions[4]),
            "isShooting" : float(actions[5]),
        }

        return action_dict
        



        