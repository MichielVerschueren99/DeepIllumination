import os

if __name__ == "__main__":

    os.system("python train.py --dataset primitive_room_ffextra --n_epoch 40 --gt_name indirect --seed 201")
    os.system("python train.py --dataset primitive_room_ffextra --n_epoch 40 --gt_name indirect --seed 202")
    os.system("python train.py --dataset primitive_room_ffextra --n_epoch 40 --gt_name indirect --seed 203")

    print("ALL TRAINING RUNS COMPLETED")
