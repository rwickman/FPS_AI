import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import os
import random

from state_history import StateHistory
from config import *

def map_action(action_dict: dict):
    """Map an action dict to an action index."""
    action = [
        action_to_idx["mouse_x"][str(action_dict["xMouse"])],
        action_to_idx["mouse_y"][str(action_dict["yMouse"])],
        action_to_idx["move"][(str(action_dict["xMove"]), str(action_dict["yMove"]))],
        int(action_dict["isRunning"]),
        int(action_dict["isJumping"]),
        int(action_dict["isShooting"]),
    ]

    return torch.tensor(action, device=device)

def map_state(state_dict: dict) -> tuple:
    """Convert the state dict into a state and mask tensor."""    
    user_state = state_dict["position"] + state_dict["rotation"]
    enemy_states = []

    for enemy_state in state_dict["enemies"]:
        enemy_states += enemy_state["position"]
        enemy_states += enemy_state["rotation"]

    state_list = user_state + enemy_states

    state = torch.zeros(STATE_SIZE, device=device)
    state[:len(state_list)] = torch.tensor(state_list, device=device)
    
    mask = torch.zeros(ENC_STATE_SIZE, device=device)
    mask[1 + len(state_dict["enemies"]):] = 1

    # Create state mask
    return state, mask 

def load_data():
    data_files = os.listdir(replay_episode)
    actions, states, masks = [], [], []
    for data_file in data_files:
        if "meta" in data_file:
            continue
        exp_dict_list = torch.load(os.path.join(replay_episode, data_file))
        cur_actions, cur_states, cur_masks = load_replays(exp_dict_list)
        actions += cur_actions
        states += cur_states
        masks += cur_masks
    
    return actions, states, masks

def load_replays(exp_dict_list):
    """Convert the actions and states to training data."""
    actions = []
    states = []
    masks = []

    # Map them to int actions
    for exp_dict in exp_dict_list:
        state_history = StateHistory()
        for i in range(len(exp_dict["actions"])):
            state_dict = exp_dict["states"][i]
            action_dict = exp_dict["actions"][i]
             
            action_idx = map_action(action_dict)
            
            # # Filter out do nothing actions
            # if action_idx == 0:
            #     continue

            #  Map the action to index
            actions.append(action_idx)

            # Convert the state into tensor
            state, mask = map_state(state_dict)

            # Augment the state with additional timesteps
            state, mask = state_history.update_state(state, mask)

            states.append(state)
            masks.append(mask)

    return actions, states, masks
    

class ReplayDataset(Dataset):
    """Dataset for player replay experiences."""
    def __init__(self, actions, states, masks):
        self.actions = actions
        self.states = states
        self.masks = masks
    
    def __len__(self):
        return len(self.states)
    
    def __getitem__(self, idx):
        return self.actions[idx], self.states[idx], self.masks[idx]

def get_dataloader():
    
    actions, states, masks = load_data()
    valid_idx = len(actions) - int(len(actions) * valid_split)
    
    # Shuffle the data
    trajs = list(zip(actions, states, masks))
    random.Random(4).shuffle(trajs)
    actions, states, masks = zip(*trajs)

    # Split into train and validation
    train_replay_dataset = ReplayDataset(actions[:valid_idx], states[:valid_idx], masks[:valid_idx])
    val_replay_dataset = ReplayDataset(actions[valid_idx:], states[valid_idx:], masks[valid_idx:])

    
    print("Number of training examples", len(train_replay_dataset))
    print("Number of validation examples", len(val_replay_dataset))

    train_dataloader = DataLoader(
        train_replay_dataset,
        batch_size=batch_size,
        shuffle=True)
    val_dataloader = DataLoader(
        val_replay_dataset,
        batch_size=batch_size,
        shuffle=True)
    
    
    return train_dataloader, val_dataloader