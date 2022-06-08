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

    action_vec = [
        float(action_dict["xMouse"]),
        float(action_dict["yMouse"]),
        float(action_dict["xMove"]),
        float(action_dict["yMove"])]
    
    if int(action_dict["isRunning"]) == 0:
        action_vec.append(0)
        action_vec.append(1)
    else:
        action_vec.append(1)
        action_vec.append(0)

    if int(action_dict["isJumping"]) == 0:
        action_vec.append(0)
        action_vec.append(1)
    else:
        action_vec.append(1)
        action_vec.append(0)

    if int(action_dict["isShooting"]) == 0:
        action_vec.append(0)
        action_vec.append(1)
    else:
        action_vec.append(1)
        action_vec.append(0)
    

    return torch.tensor(action, device=device), action_vec

def map_state(state_dict: dict, action_vec: torch.Tensor, reward: float) -> tuple:
    """Convert the state dict into a state and mask tensor."""    
    user_state = state_dict["position"] + state_dict["rotation"]
    user_state.append(state_dict["health"])
    enemy_states = []

    for enemy_state in state_dict["enemies"]:
        enemy_states += enemy_state["position"]
        enemy_states += enemy_state["rotation"]
        enemy_states.append(enemy_state["health"])

    state_list = action_vec + user_state + [reward] + enemy_states

    state = torch.zeros(STATE_SIZE, device=device)
    state[:len(state_list)] = torch.tensor(state_list, device=device)
    
    mask = torch.zeros(ENC_STATE_SIZE, device=device)
    mask[TRAJ_SIZE + len(state_dict["enemies"]):] = 1

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
    non_zero_count = 0

    # Map them to int actions
    for exp_dict in exp_dict_list:
        prev_action_vec = default_action
        state_history = StateHistory()
        print("\n")
        for i in range(len(exp_dict["actions"])):
            state_dict = exp_dict["states"][i]
            action_dict = exp_dict["actions"][i]
            return_to_go = -sum(exp_dict["rewards"][i:])
            
            print("return_to_go", return_to_go)
             
            action_idx, action_vec = map_action(action_dict)
            
            # # Filter out do nothing actions
            # if action_idx == 0:
            #     continue

            #  Map the action to index
            if action_idx[0] == 0 and action_idx[1] == 0 and action_idx[2] == 4 and action_idx[-1] == 0:
                non_zero_count += 1
                if non_zero_count < 3:
                    continue
                else:
                    non_zero_count = 0
                
            
            actions.append(action_idx)

            # Convert the state into tensor
            state, mask = map_state(state_dict, prev_action_vec, return_to_go)
            prev_action_vec = action_vec

            # Augment the state with additional timesteps
            state, mask = state_history.update_state(state, mask)
            

            states.append(state)
            masks.append(mask)
            if return_to_go == 0:
                break

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