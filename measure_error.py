import argparse
import os
from torch.utils.tensorboard import SummaryWriter
import piqa
import torch
import torch.nn as nn
from torch.autograd import Variable
from piqa.utils.functional import gaussian_kernel
from model import G
from util import is_image, load_image, save_image

buffer_names = ['albedo', 'direct', 'normal', 'depth']
epoch_range = (0, 24)

if __name__ == "__main__":

    directory = os.getcwd()

    parser = argparse.ArgumentParser(description='DeepRendering-implementation')
    parser.add_argument('--dataset', required=True, help='unity')
    parser.add_argument('--run', type=str, required=True, help='run folder')
    parser.add_argument('--gt_name', type=str, default="gt", help='name of gt folder')
    parser.add_argument('--n_channel_input', type=int, default=3, help='input channel')
    parser.add_argument('--n_channel_output', type=int, default=3, help='output channel')
    parser.add_argument('--n_generator_filters', type=int, default=64, help="number of generator filters")
    opt = parser.parse_args()

    gt_name = opt.gt_name

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    for epoch in range(epoch_range[0], epoch_range[1] + 1):
        print("Measuring_epoch_{}_performance...".format(epoch))
        netG_model = torch.load(os.getcwd() + '\\checkpoint\\{}\\{}\\netG_model_epoch_{}.pth'.format(opt.dataset, opt.run, str(epoch)), map_location=device)
        netG = G(opt.n_channel_input * 4, opt.n_channel_output, opt.n_generator_filters, netG_model['norm_mean_G'], netG_model['norm_std_G'], device)
        netG.load_state_dict(netG_model['state_dict_G'])
        root_dir = os.getcwd() + '\\dataset\\{}\\val\\'.format(opt.dataset) #TODO veranderd naar val!!!
        image_dir = os.getcwd() + '\\dataset\\{}\\val\\{}'.format(opt.dataset, buffer_names[0])
        image_filenames = [x for x in os.listdir(image_dir) if is_image(x)]

        writer = SummaryWriter("performance" + '/' + opt.dataset + '/' + opt.run)

        mean_MSE_clamped = 0.0
        mean_SSIM_clamped = 0.0
        MSE = nn.MSELoss()
        kernel = gaussian_kernel(11, sigma=1.5).repeat(3, 1, 1).to(device)
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

            out_G = netG(torch.cat(buffers, 1))

            nn_result = netG.unnormalize_gt(out_G)

            nn_result[nn_result < 0] = 0

            # als het netwerk naar indirect optimaliseerd is gt alleen indirect
            if not gt_name == 'gt':
                nn_result = torch.add(nn_result, buffers[buffer_names.index("direct")].data[0])
                full_gi_gt = Variable(load_image(root_dir + 'gt' + '\\' + image_name)).view(1, -1, 256, 256).to(device)
                mean_MSE_clamped += MSE(nn_result, full_gi_gt).item()
                max = torch.max(torch.cat((nn_result, full_gi_gt), 1)).item()
                mean_SSIM_clamped += piqa.ssim.ssim(nn_result, full_gi_gt, kernel, value_range=max)[0].item()
            else:
                mean_MSE_clamped += MSE(nn_result, gt).item()
                max = torch.max(torch.cat((nn_result, gt), 1)).item()
                mean_SSIM_clamped += piqa.ssim.ssim(nn_result, gt, kernel, value_range=max)[0].item()  # TODO max?


        writer.add_scalar('output_MSE', mean_MSE_clamped / len(image_filenames), epoch)
        writer.add_scalar('output_SSIM', mean_SSIM_clamped / len(image_filenames), epoch)
