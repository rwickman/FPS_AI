import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MAX_ENEMIES = 2

# Size of the agent state
AGENT_INP_SIZE = 8

# Size of the target state
ENEMY_INP_SIZE = 8

ACTION_VEC_SIZE = 10


# Trajectory size (state, action, reward)
TRAJ_SIZE = 3

"""Model hyperparameters"""
hidden_size = 64
emb_size = 128
dff=256
inp_timesteps = 14
num_heads=4
drop_rate=0.1
num_enc_layers=6
lr = 3e-4

# The number of target states + the agent state
ENC_STATE_SIZE = TRAJ_SIZE + MAX_ENEMIES

RETURN_SIZE = 1

default_action = [0, ]

NUM_NONTARGET_EMBS = 2

STATE_SIZE = AGENT_INP_SIZE + ACTION_VEC_SIZE + RETURN_SIZE + ENEMY_INP_SIZE * MAX_ENEMIES

replay_episode = "/media/data/code/KillerAI/Killer AI/Assets/Scripts/python/experiences/"

HEADER_LEN  = 8

PORT = 12001
batch_size = 64
valid_split = 0.1
save_dir = "/media/data/code/KillerAI/Killer AI/Assets/Scripts/python/models"
load = False
epochs = 100

ACTION_DIMS = [
    9, # mouse_x
    9, # mouse_y
    9, # move
    2, # isRunning
    2, # isJumping
    2, # isShooting
]
mouse_pos = ["0.0", "0.1", "0.33", "0.66", "1.0", "-0.1", "-0.33", "-0.66", "-1.0"]

move_pos = ["1.0", "0.0", "-1.0"]

action_to_idx = {
    "move" : {},
    "mouse_x": {},
    "mouse_y": {},
}

cur_iter = 0
for key in ["mouse_x", "mouse_y"]:
    cur_iter = 0
    for i in range(len(mouse_pos)):
        action_to_idx[key][mouse_pos[i]] = cur_iter 
        cur_iter += 1

cur_iter = 0
for i in range(len(move_pos)):
    for j in range(len(move_pos)):
        action_to_idx["move"][(move_pos[i], move_pos[j])] = cur_iter 
        cur_iter += 1

move_list = list(action_to_idx["move"].keys())

print(action_to_idx)



# ACTIONS = []
# for i in [0, 1, -1]:
#     for j in [0, 1, -1]:
#         for k in [False, True]:
#             # (yaw, pitch, shooting)
#             ACTIONS.append((i, j, k))
# print(len(ACTIONS))

# NUM_ACTIONS = len(ACTIONS)
