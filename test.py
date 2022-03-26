import argparse
import os

import torch
from torch.autograd import Variable

from model import G
from util import is_image, load_image, save_image

if __name__ == "__main__":

    directory = os.getcwd()

    parser = argparse.ArgumentParser(description='DeepRendering-implementation')
    parser.add_argument('--dataset', required=True, help='unity')
    parser.add_argument('--model', type=str, required=True, help='model file')
    parser.add_argument('--add_direct_illumination', type=bool, default=False, help='add direct illumination to saved image?')
    parser.add_argument('--n_channel_input', type=int, default=3, help='input channel')
    parser.add_argument('--n_channel_output', type=int, default=3, help='output channel')
    parser.add_argument('--n_generator_filters', type=int, default=64, help="number of generator filters")
    opt = parser.parse_args()

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    netG_model = torch.load(os.getcwd() + '\\checkpoint\\{}'.format(opt.model), map_location=device)
    netG = G(opt.n_channel_input * 4, opt.n_channel_output, opt.n_generator_filters, netG_model['norm_mean_G'], netG_model['norm_std_G'], device)
    netG.load_state_dict(netG_model['state_dict_G'])
    root_dir = os.getcwd() + '\\dataset\\{}\\test\\'.format(opt.dataset)
    image_dir = os.getcwd() + '\\dataset\\{}\\test\\albedo'.format(opt.dataset)
    image_filenames = [x for x in os.listdir(image_dir) if is_image(x)]

    for image_name in image_filenames:
        albedo_image = load_image(root_dir + 'albedo\\' + image_name)
        direct_image = load_image(root_dir + 'direct\\' + image_name)
        normal_image = load_image(root_dir + 'normal\\' + image_name)
        depth_image = load_image(root_dir + 'depth\\' + image_name)
        gt_image = load_image(root_dir + 'gt\\' + image_name)

        albedo = Variable(albedo_image).view(1, -1, 256, 256).to(device)
        direct = Variable(direct_image).view(1, -1, 256, 256).to(device)
        normal = Variable(normal_image).view(1, -1, 256, 256).to(device)
        depth = Variable(depth_image).view(1, -1, 256, 256).to(device)

        netG = netG.to(device)

        out = netG(torch.cat((albedo, direct, normal, depth), 1))
        out_img_normalized = out.data[0]
        out_img = netG.unnormalize_gt(out_img_normalized).cpu()

        if not os.path.exists("result"):
            os.mkdir("result")
        if not os.path.exists(os.path.join("result", opt.dataset)):
            os.mkdir(os.path.join("result", opt.dataset))
        save_image(out_img, "result\\{}\\{}".format(opt.dataset, image_name))
