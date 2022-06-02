import os
import argparse

from config import save_dir
from trainer import ImitationTrainer
from imitation_policy import ImitationPolicy
from imitation_worker import ImitationWorker

def main(args):
    if args.env:
        policy = ImitationPolicy()
        worker = ImitationWorker(policy)
        worker.start()
    else:
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        
        policy = ImitationPolicy(is_training=True)
            
        trainer = ImitationTrainer(policy)
        trainer.train()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", action="store_true",
                    help="Run in environment.")

    args = parser.parse_args()
    main(args) 
    