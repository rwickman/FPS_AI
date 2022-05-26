import argparse
import socket, sys, os, json
import torch

from config import *

class RecordPlayer:
    def __init__(self, num_episodes):
        self.num_episodes = num_episodes

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", PORT))
            s.listen(20)
            print("WAITING TO ACCEPT")
            self.conn, client_adr = s.accept()
            print("Connected by", client_adr)
            self.store_episodes()

    def store_episodes(self):
        exps = []
        for i in range(self.num_episodes):
            print("WAITING TO RECEIVE")
            data_header = self.conn.recv(HEADER_LEN)
            print("GOT DATA HEADER")
            # Get the length of the data
            data_len = int(data_header.decode().rstrip("\x00"))
            
            # Read the packet data
            data = self.conn.recv(data_len, socket.MSG_WAITALL)
            
            if not data:
                # Data was not present, so must be done
                break
            
            env_dic = json.loads(data)
            exps.append(env_dic)
            print("env_dic", env_dic)
            print("env_dic", len(env_dic))


        self.save(exps)
        
    def save(self, exps):
        torch.save(exps, f"experiences/player_{self.num_episodes}_episodes.pt")


def main(args):
    record_player = RecordPlayer(args.num_episodes)
    record_player.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_episodes", type=int, default=1,
        help="Number of training episodes.")
    
    main(parser.parse_args())
