import argparse
import os

import torch
from torch.autograd import Variable

from model import G
from util import is_image, load_image, save_image

buffer_names = ['albedo', 'direct', 'normal', 'depth']
phis = [0, 0, 90, 180, 270]
thetas = [0, 45, 45, 45, 45]

for i in range(0, len(phis)):
    buffer_names.append("albedo2p{}t{}".format(phis[i], thetas[i]))
    buffer_names.append("normal2p{}t{}".format(phis[i], thetas[i]))

if __name__ == "__main__":

    directory = os.getcwd()

    parser = argparse.ArgumentParser(description='DeepRendering-implementation')
    parser.add_argument('--dataset', required=True, help='unity')
    parser.add_argument('--model', type=str, required=True, help='model file')
    parser.add_argument('--gt_name', type=str, default="gt", help='name of gt folder')
    parser.add_argument('--do_val', type=bool, default=True, help='run on validation set instead of test set')
    parser.add_argument('--n_channel_input', type=int, default=3, help='input channel')
    parser.add_argument('--n_channel_output', type=int, default=3, help='output channel')
    parser.add_argument('--n_generator_filters', type=int, default=64, help="number of generator filters")
    opt = parser.parse_args()

    gt_name = opt.gt_name

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    if opt.do_val:
        root_dir = os.getcwd() + '\\dataset\\{}\\val\\'.format(opt.dataset)
        # buffer_names = os.listdir(root_dir)
        # buffer_names.remove("gt")
        # buffer_names.remove("indirect")
        image_dir = os.getcwd() + '\\dataset\\{}\\val\\{}'.format(opt.dataset, buffer_names[0])
    else:
        root_dir = os.getcwd() + '\\dataset\\{}\\test\\'.format(opt.dataset)
        image_dir = os.getcwd() + '\\dataset\\{}\\test\\{}'.format(opt.dataset, buffer_names[0])
    image_filenames = [x for x in os.listdir(image_dir) if is_image(x)]

    netG_model = torch.load(os.getcwd() + '\\checkpoint\\{}'.format(opt.model), map_location=device)
    netG = G(opt.n_channel_input * len(buffer_names), opt.n_channel_output, opt.n_generator_filters, netG_model['norm_mean_G'], netG_model['norm_std_G'], device)
    netG.load_state_dict(netG_model['state_dict_G'])

    for image_name in image_filenames:

        images = []
        for buffer_name in buffer_names:
            images.append(load_image(root_dir + buffer_name + '\\' + image_name))
        gt_image = load_image(root_dir + gt_name + '\\' + image_name)

        buffers = []
        for image in images:
            buffers.append(Variable(image).view(1, -1, 256, 256).to(device))
        gt = Variable(gt_image).view(1, -1, 256, 256).to(device)

        netG = netG.to(device)

        out = netG(torch.cat(buffers, 1))
        out_img_normalized = out.data[0]
        out_img = netG.unnormalize_gt(out_img_normalized)

        if not gt_name == 'gt':
            out_img = torch.add(out_img, buffers[buffer_names.index("direct")].data[0])

        out_img = out_img.cpu()

        if not os.path.exists("result"):
            os.mkdir("result")
        if not os.path.exists(os.path.join("result", opt.dataset)):
            os.mkdir(os.path.join("result", opt.dataset))
        if not os.path.exists(os.path.join(os.path.join("result", opt.dataset), opt.model[:-4])):
            os.mkdir(os.path.join(os.path.join("result", opt.dataset), opt.model[:-4]))
        if opt.do_val:
            save_image(out_img, "result\\{}\\{}\\{}".format(opt.dataset, opt.model[:-4], "val" + image_name))
        else:
            save_image(out_img, "result\\{}\\{}\\{}".format(opt.dataset, opt.model[:-4], image_name))
