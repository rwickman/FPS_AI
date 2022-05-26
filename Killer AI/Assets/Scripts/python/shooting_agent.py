import torch
import torch.nn as nn
import torch.nn.functional as F
import json, socket, threading
import random

from dqn_policy import DQNTrainer
from storage import Experience

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class AgentServer:
    def __init__(self, args):
        self.args = args

    def start(self):
        # Create socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", self.args.port))
            s.listen(20)
            print("Starting accepting")
            while True:
                print("WAITING TO ACCEPT")
                conn, client_adr = s.accept()
                print("ACCEPTED")
                agent = ShootingAgent(self.args, conn)
                agent.run()


# class ShootingAgent:
#     def __init__(self, args, conn):
#         self.args = args
#         self.conn = conn
#         self._model = DQNTrainer(args)
        
#     def receive_state(self) -> dict:
#         # Read the packet header
#         data_header = self.conn.recv(self.args.header_len)

#         # Get the length of the data
#         data_len = int(data_header.decode().rstrip("\x00"))

#         # Read the packet data
#         data = self.conn.recv(data_len, socket.MSG_WAITALL)

#         state_dict = json.loads(data)

#         #state_dict["state"] = #torch.tensor(state_dict["state"], device=device)
#         #state_dict
        
#         return self._resolve_state(state_dict), state_dict["done"], state_dict["reward"]

#     def send_action(self, action_dict):
#         action_json_str = json.dumps(action_dict)

#         action_len_str = str(len(action_json_str))

#         # Pad to fixed size
#         action_len_str = (self.args.header_len - len(action_len_str)) * "0" + action_len_str
        
#         # Send the action
#         self.conn.send(action_len_str.encode())
#         self.conn.send(action_json_str.encode())
#         # print("SENDING ACTION")


#     def send_end(self):
#         print("SENDING END MSG")
#         # Send empty message to indicate readiness for next episode
#         end_header = "0" * self.args.header_len
#         self.conn.send(end_header.encode())

#     def _resolve_state(self, state_dict: dict) -> torch.Tensor:
#         state_data = [
#             state_dict["pitch"],
#             state_dict["yaw"],
#             state_dict["delay"]
#         ]
        
#         for target in state_dict["targets"]:
#             for i in range(3, 6):
#                 target[i] = target[i]/360

#             state_data = state_data + target
        
#         return torch.tensor(state_data, device=device).unsqueeze(0)
        

#     def _resolve_action(self, action) -> dict:
#         """Convert action sampled from policy to action_dict for agent to understand."""
#         action_dict = {
#             "yaw": 0.0,
#             "pitch": 0.0,
#             "shoot" : 0.0
#         }

#         if action == 0:
#             action_dict["yaw"] = 0.1
#         elif action == 1:
#             action_dict["yaw"] = -0.1
#         elif action == 2:
#             action_dict["pitch"] = 0.1
#         elif action == 3:
#             action_dict["pitch"] = -0.1
#         elif action == 4:
#             action_dict["shoot"] = 1.0
#         else:
#             raise Exception("Invalid action")
        
#         return action_dict

#     def run(self):
#         for e_i in range(self.args.episodes):
#             ep_reward = 0
#             num_steps = 0
#             prev_state = None
#             while True:
#                 # Get the state from the Unity agent
#                 state, done, reward = self.receive_state()
#                 reward = reward

#                 num_steps += 1
#                 ep_reward += reward
#                 #print("state", state)
#                 if prev_state is not None:
#                     if not done:
#                         self._model.add_exp(
#                             Experience(
#                                 prev_state,
#                                 action,
#                                 reward,
#                                 state)
#                         )
#                     else:
#                         self._model.add_exp(
#                             Experience(
#                                 prev_state,
#                                 action,
#                                 reward)
#                         )
#                         break
                
#                 if self._model.is_train_ready() and num_steps % self.args.update_step == 0:
#                     self._model.train()
                

#                 # Get action prediction from model
#                 action = self._model(state)
                

#                 action_dict = self._resolve_action(action)
        
#                 # Send action to the Unity agent
#                 self.send_action(action_dict)
#                 prev_state = state
            
#             self._model.reset(ep_reward)
            
#             print("TOTAL EPISODE REWARD:",ep_reward)
#             print("EPISODE STEPS: ", num_steps)
#             # if e_i >= 2:
#             #     for _ in range(self.args.train_iter):
#             #         self._model.train()
            
#             self._model.save()
        
#             # Reset for next episode
#             self.send_end()
            
