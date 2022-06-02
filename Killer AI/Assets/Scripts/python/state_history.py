import torch

from config import *

class StateHistory:
    def __init__(self):
        self.state_history = torch.zeros(inp_timesteps, STATE_SIZE, device=device)
        self.mask_history = torch.zeros(inp_timesteps, ENC_STATE_SIZE, device=device)
        
    def update_state(self, state: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Augment the state with the history of states."""
        self.state_history = self.state_history.roll(-1, dims=0)
        self.mask_history = self.mask_history.roll(-1, dims=0)
        self.state_history[-1] = state        
        self.mask_history[-1] = mask
    
        return self.state_history, self.mask_history