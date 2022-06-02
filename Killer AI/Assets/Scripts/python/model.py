import torch
import torch.nn as nn
from config import *
# Model

class Encoder(nn.Module):
    """Encoder for agent information."""
    def __init__(self, inp_size):
        super().__init__()

        self.fc1 = nn.Linear(inp_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, emb_size)
        #self.norm_1 = nn.LayerNorm(self.args.hidden_size, eps=1e-6)
        self.act1 = nn.GELU()
        self.dropout_1 = nn.Dropout(drop_rate)


    def forward(self, x) -> torch.Tensor:
        x = self.fc1(x)
        # x = self.norm_1(x)
        x = self.act1(x)
        x = self.dropout_1(x)
        x = self.fc2(x)
        # x = self.norm_2(x)
        return x


class ImitationModel(nn.Module):
    def __init__(self, use_softmax=False):
        super().__init__()
        self.agent_enc = Encoder(AGENT_INP_SIZE)
        self.enemy_enc = Encoder(ENEMY_INP_SIZE)
        
        # Embedding for the timestep position
        self.pos_embs = nn.Parameter(torch.randn(1, 1, inp_timesteps, emb_size))
        self.pred_emb =  nn.Parameter(torch.randn(1, 1, emb_size))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=emb_size,
            nhead=num_heads,
            dim_feedforward=dff,
            dropout=drop_rate,
            batch_first=True)
        self.enc = nn.TransformerEncoder(encoder_layer, num_enc_layers)
        
        self.fc_outs = []
        for action_dim in ACTION_DIMS:
            self.fc_outs.append(nn.Linear(emb_size, action_dim))
        
        self.fc_outs = nn.ModuleList(self.fc_outs)

        self.softmax_out = nn.Softmax(dim=-1)
        self.use_softmax = use_softmax
        
        
    def forward(self,
                state: torch.Tensor,
                mask: torch.Tensor = None) -> torch.Tensor:
        batch_size = state.shape[0]

        # Break into individual parts
        agent_state = state[:, :, :AGENT_INP_SIZE].unsqueeze(1)
        target_state = state[:, :, AGENT_INP_SIZE:].reshape(batch_size, MAX_ENEMIES, inp_timesteps, ENEMY_INP_SIZE)

        # Get embeddings
        agent_emb = self.agent_enc(agent_state)
        target_embs = self.enemy_enc(target_state)
        
        
        embs = torch.cat((agent_emb, target_embs), 1)
        embs = embs + self.pos_embs

        
        
        embs = embs.reshape(batch_size, -1, emb_size)
        mask = mask.reshape(batch_size, -1)
        # Update mask to include

        mask = torch.cat((mask, torch.zeros(batch_size, 1, device=device)), -1)                
        embs = torch.cat((embs, self.pred_emb.repeat(batch_size, 1, 1)), 1)

        
        embs = self.enc(embs, src_key_padding_mask=mask)


        # Get the action distribution
        pred_outs = []
        for fc_out in self.fc_outs:
            pred_out = fc_out(embs[:, -1])
            if self.use_softmax:
                pred_out = self.softmax_out(pred_out)
            pred_outs.append(pred_out)

        return pred_outs


