import os

if __name__ == "__main__":

    os.system("python train.py --dataset primitive_room_ff2 --n_epoch 40 --gt_name indirect --seed 301")
    os.system("python train.py --dataset primitive_room_ff2 --n_epoch 40 --gt_name indirect --seed 302")
    os.system("python train.py --dataset primitive_room_ff2 --n_epoch 40 --gt_name indirect --seed 303")

    os.system("python train.py --dataset primitive_room_ff3 --n_epoch 40 --gt_name indirect --seed 304")
    os.system("python train.py --dataset primitive_room_ff3 --n_epoch 40 --gt_name indirect --seed 305")
    os.system("python train.py --dataset primitive_room_ff3 --n_epoch 40 --gt_name indirect --seed 306")

    print("ALL TRAINING RUNS COMPLETED")
