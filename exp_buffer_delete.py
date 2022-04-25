import os

import train


if __name__ == "__main__":

    for _ in range(0, 3):
        os.system("python train.py --dataset primitive_room_f1_no_albedo --n_epoch 25 --seed 1")

    for _ in range(0, 3):
        os.system("python train.py --dataset primitive_room_f1_no_depth --n_epoch 25 --seed 2")

    for _ in range(0, 3):
        os.system("python train.py --dataset primitive_room_f1_no_direct --n_epoch 25 --seed 3")

    for _ in range(0, 3):
        os.system("python train.py --dataset primitive_room_f1_no_normal --n_epoch 25 --seed 4")

    print("ALL TRAINING RUNS COMPLETED")
