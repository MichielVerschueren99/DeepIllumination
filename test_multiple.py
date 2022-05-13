import os

import train


if __name__ == "__main__":


    # DELBUFFER
    # os.system("python test.py --dataset test_setups_no_albedo --model DEL_no_albedo_24.pth")
    # os.system("python test.py --dataset test_setups_no_depth --model DEL_no_depth_24.pth")
    # os.system("python test.py --dataset test_setups_no_direct --model DEL_no_direct_24.pth")
    # os.system("python test.py --dataset test_setups_no_normal --model DEL_no_normal_24.pth")

    # GIvsIND
    # os.system("python test.py --dataset test_setups --model GIvsIND_GI_24.pth")
    # os.system("python test.py --dataset test_setups --model GIvsIND_IND_24.pth --gt_name indirect")
    # os.system("python test.py --dataset primitive_room_ff --model GIvsIND_GI_24.pth")
    # os.system("python test.py --dataset primitive_room_ff --model GIvsIND_IND_24.pth --gt_name indirect")
    # os.system("python test.py --dataset primitive_room_ff --model GIvsIND_GI_24.pth")
    # os.system("python test.py --dataset primitive_room_ff --model GIvsIND_IND_24.pth --gt_name indirect")

    #DIFDUBBEL
    #os.system("python test.py --dataset primitive_room_ffextra --model DIF_39.pth --gt_name indirect")
    #os.system("python test.py --dataset test_setups_extra --model DIF_39.pth --gt_name indirect")
    os.system("python test.py --dataset primitive_room_ffextra --model DIF_39.pth --gt_name indirect")

    print("ALL TEST RUNS COMPLETED")
