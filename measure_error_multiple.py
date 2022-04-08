import os


if __name__ == "__main__":

    runs = [f.name for f in os.scandir("D:\\Thesis\\DeepIllumination\\checkpoint\\primitive_room_f1") if f.is_dir()]

    for i in range(0, 5):
        os.system("python measure_error.py --dataset primitive_room_f1 --run {}".format(runs[i]))

    for i in range(0, 5):
        os.system("python measure_error.py --dataset primitive_room_f1 --run {} --gt_name indirect".format(runs[5 + i]))

    print("ALL MEASURING RUNS COMPLETED")
