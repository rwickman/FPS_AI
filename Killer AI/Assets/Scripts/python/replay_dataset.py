import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import os

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
    temp_state = {'position': [10.499, 0.962, 1.12525835e-18], 'rotation': [0.0, 0.0, 0.0, 1.0], 'enemies': [{'position': [11.4103689, -4.76837158e-07, 7.02], 'rotation': [0.0, 0.06450648, 0.0, 0.9979173]}]}
    
    user_state = [state_dict["yaw"], state_dict["pitch"]]
    target_states = []

    for target_state in state_dict["enemies"]:
        target_states += target_state["position"]
        target_states += target_state["rotation"]

    state_list = user_state + target_states

    state = torch.zeros(STATE_SIZE, device=device)
    state[:len(state_list)] = torch.tensor(state_list, device=device)
    
    mask = torch.zeros(ENC_STATE_SIZE, device=device)
    mask[1 + len(state_dict["enemies"]):] = 1

    # Create state mask
    return state, mask 

def load_data(args):
    data_files = os.listdir(args.replay_episode)
    actions, states, masks = [], [], []
    for data_file in data_files:
        if "meta" in data_file:
            continue
        exp_dict_list = torch.load(os.path.join(args.replay_episode, data_file))
        cur_actions, cur_states, cur_masks = load_replays(args, exp_dict_list)
        actions += cur_actions
        states += cur_states
        masks += cur_masks
    
    return actions, states, masks

def load_replays(args, exp_dict_list):
    """Convert the actions and states to training data."""
    # exp_dict_list = torch.load(args.replay_episode)
    actions = []
    states = []
    masks = []

    # Map them to int actions
    for exp_dict in exp_dict_list:
        state_history = StateHistory(args)
        for i in range(len(exp_dict["actions"])):
            state_dict = exp_dict["states"][i]
            action_dict = exp_dict["actions"][i]
             
            action_idx = map_action(action_dict)
            
            # Filter out do nothing actions
            if action_idx == 0:
                continue

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

def get_dataloader(args):
    
    actions, states, masks = load_data(args)
    valid_idx = len(actions) - int(len(actions) * args.valid_split)
    
    
    train_replay_dataset = ReplayDataset(actions[:valid_idx], states[:valid_idx], masks[:valid_idx])
    val_replay_dataset = ReplayDataset(actions[valid_idx:], states[valid_idx:], masks[valid_idx:])

    
    print("Number of training examples", len(train_replay_dataset))
    print("Number of validation examples", len(val_replay_dataset))

    train_dataloader = DataLoader(
        train_replay_dataset,
        batch_size=args.batch_size,
        shuffle=True)
    val_dataloader = DataLoader(
        val_replay_dataset,
        batch_size=args.batch_size,
        shuffle=True)
    
    
    return train_dataloader, val_dataloader