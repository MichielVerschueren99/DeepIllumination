import os

if __name__ == "__main__":

    os.system("python train.py --dataset primitive_room_f1dot5 --n_epoch 40 --gt_name indirect --seed 1")
    os.system("python train.py --dataset primitive_room_f1dot5 --n_epoch 40 --gt_name indirect --seed 2")
    os.system("python train.py --dataset primitive_room_f1dot5 --n_epoch 40 --gt_name indirect --seed 3")
    os.system("python train.py --dataset primitive_room_f1dot5 --n_epoch 40 --gt_name indirect --seed 4")
    os.system("python train.py --dataset primitive_room_f1dot5 --n_epoch 40 --gt_name indirect --seed 5")

    print("ALL TRAINING RUNS COMPLETED")
