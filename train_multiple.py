import os

import train


if __name__ == "__main__":

    for _ in range(0, 5):
        os.system("python train.py --dataset primitive_room_f1 --n_epoch 30")

    for _ in range(0, 5):
        os.system("python train.py --dataset primitive_room_f1 --n_epoch 30 --gt_name indirect")

    print("ALL TRAINING RUNS COMPLETED")