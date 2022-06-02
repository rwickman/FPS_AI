
import json, socket, threading

from config import *

class ImitationWorker:
    def __init__(self, policy):
        self.policy = policy
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", PORT))
            s.listen(20)
            print("Starting accepting")
            print("WAITING TO ACCEPT")
            self.conn, client_adr = s.accept()
            print("Connected by", client_adr)
            self.run()

    def receive_state(self) -> dict:
        # Read the packet header
        # print("WAITING FOR STATE")
        data_header = self.conn.recv(HEADER_LEN)

        # Get the length of the data
        data_len = int(data_header.decode().rstrip("\x00"))

        # Read the packet data
        data = self.conn.recv(data_len, socket.MSG_WAITALL)

        state_dict = json.loads(data)
        state_dict = state_dict["state"] 
        
        return state_dict

    def send_action(self, action_dict):
        action_json_str = json.dumps(action_dict)

        action_len_str = str(len(action_json_str))

        # Pad to fixed size
        action_len_str = (HEADER_LEN - len(action_len_str)) * "0" + action_len_str
        
        # Send the action
        self.conn.send(action_len_str.encode())
        self.conn.send(action_json_str.encode())

    def run(self):
        while True:
            state = self.receive_state()

            action = self.policy(state)
            self.send_action(action)






