import os

import train


if __name__ == "__main__":

    os.system("python train.py --dataset primitive_room_ff_no_albedo --n_epoch 25 --seed 101")
    os.system("python train.py --dataset primitive_room_ff_no_albedo --n_epoch 25 --seed 102")
    os.system("python train.py --dataset primitive_room_ff_no_albedo --n_epoch 25 --seed 103")

    os.system("python train.py --dataset primitive_room_ff_no_depth --n_epoch 25 --seed 104")
    os.system("python train.py --dataset primitive_room_ff_no_depth --n_epoch 25 --seed 105")
    os.system("python train.py --dataset primitive_room_ff_no_depth --n_epoch 25 --seed 106")

    os.system("python train.py --dataset primitive_room_ff_no_direct --n_epoch 25 --seed 107")
    os.system("python train.py --dataset primitive_room_ff_no_direct --n_epoch 25 --seed 108")
    os.system("python train.py --dataset primitive_room_ff_no_direct --n_epoch 25 --seed 109")

    os.system("python train.py --dataset primitive_room_ff_no_normal --n_epoch 25 --seed 110")
    os.system("python train.py --dataset primitive_room_ff_no_normal --n_epoch 25 --seed 111")
    os.system("python train.py --dataset primitive_room_ff_no_normal --n_epoch 25 --seed 112")

    print("ALL TRAINING RUNS COMPLETED")
