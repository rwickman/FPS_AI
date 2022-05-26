import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MAX_ENEMIES = 10

# Size of the agent state
AGENT_INP_SIZE = 2

# Size of the target state
ENEMY_INP_SIZE = 7

"""Model hyperparameters"""
hidden_size = 64
emb_size = 128
dff=384
inp_timesteps = 14
num_heads=4
drop_rate=0.1
num_enc_layers=4

# The number of target states + the agent state
ENC_STATE_SIZE = MAX_ENEMIES + 1

NUM_NONTARGET_EMBS = 2

STATE_SIZE = AGENT_INP_SIZE + ENEMY_INP_SIZE * MAX_ENEMIES


HEADER_LEN  = 8

PORT = 12001


ACTION_DIMS = [
    9, # mouse_x
    9, # mouse_y
    4, # move
    2, # isRunning
    2, # isJumping
    2, # isShooting
]
mouse_pos = ["0.0", "0.1", "0.33", "0.66", "1", "-0.1", "-0.33", "-0.66", "-1.0"]



action_to_idx = {
    "move" : {("0.0", "0.0"): 0, ("0.0", "1.0"): 1, ("1.0", "0.0"): 2, ("1.0", "1.0"): 3},
    "mouse_x": {},
    "mouse_y": {},
} 
cur_iter = 0
for key in ["mouse_x", "mouse_y"]:
    cur_iter = 0
    for i in range(len(mouse_pos)):
        action_to_idx[key][mouse_pos[i]] = cur_iter 
        cur_iter += 1
print(action_to_idx)



# ACTIONS = []
# for i in [0, 1, -1]:
#     for j in [0, 1, -1]:
#         for k in [False, True]:
#             # (yaw, pitch, shooting)
#             ACTIONS.append((i, j, k))
# print(len(ACTIONS))

# NUM_ACTIONS = len(ACTIONS)
