import os

import train


if __name__ == "__main__":

    os.system("python train.py --dataset primitive_room_ff --n_epoch 25 --seed 1")
    os.system("python train.py --dataset primitive_room_ff --n_epoch 25 --seed 2")
    os.system("python train.py --dataset primitive_room_ff --n_epoch 25 --seed 3")

    os.system("python train.py --dataset primitive_room_ff --n_epoch 25 --gt_name indirect --seed 4")
    os.system("python train.py --dataset primitive_room_ff --n_epoch 25 --gt_name indirect --seed 5")
    os.system("python train.py --dataset primitive_room_ff --n_epoch 25 --gt_name indirect --seed 6")

    print("ALL TRAINING RUNS COMPLETED")