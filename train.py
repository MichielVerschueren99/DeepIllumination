import os
from os.path import join
import argparse
from math import log10

import torch
import torch.nn as nn
import torch.optim as optim
import torch.backends.cudnn as cudnn
import piqa
from datetime import datetime

from piqa.utils.functional import gaussian_kernel

import util
from data import DataLoaderHelper
import pytz
from torch.utils.data import DataLoader
from torch.autograd import Variable
from model import G, D, weights_init
from util import load_image, save_image
from torch.utils.tensorboard import SummaryWriter

buffer_names = ['albedo', 'direct', 'normal', 'depth', 'normal2p0t0', 'normal2p0t45', 'normal2p90t45', 'normal2p180t45', 'normal2p270t45', 'albedo2p0t0', 'albedo2p0t45', 'albedo2p90t45', 'albedo2p180t45', 'albedo2p270t45']

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DeepRendering-implemention')
    parser.add_argument('--dataset', required=True, help='output from unity')
    parser.add_argument('--dataset_directory', type=str, default="", help='give a custom dataset directory')
    parser.add_argument('--keep_every_checkpoint', type=bool, default=True,
                        help='keep the checkpoint that is generated after every epoch')
    parser.add_argument('--windows_filepaths', type=bool, default=False, help='use windows filepaths')
    parser.add_argument('--save_val_images', type=bool, default=False,
                        help='save the resulting images of the validation set')
    parser.add_argument('--gt_name', type=str, default="gt", help='name of gt folder')
    parser.add_argument('--train_batch_size', type=int, default=1, help='batch size for training') #TODO check of MSE en SSIM werken bij batch > 1
    parser.add_argument('--test_batch_size', type=int, default=1, help='batch size for testing')
    parser.add_argument('--n_epoch', type=int, default=200, help='number of iterations')
    parser.add_argument('--n_channel_input', type=int, default=3, help='number of input channels')
    parser.add_argument('--n_channel_output', type=int, default=3, help='number of output channels')
    parser.add_argument('--n_generator_filters', type=int, default=64, help='number of initial generator filters')
    parser.add_argument('--n_discriminator_filters', type=int, default=64,
                        help='number of initial discriminator filters')
    parser.add_argument('--lr', type=float, default=0.0002, help='learning rate')
    parser.add_argument('--beta1', type=float, default=0.5, help='beta1')
    parser.add_argument('--cuda', action='store_true', help='cuda')
    parser.add_argument('--resume_G', help='resume G')
    parser.add_argument('--resume_D', help='resume D')
    parser.add_argument('--workers', type=int, default=2,
                        help='number of threads for data loader')
    parser.add_argument('--seed', type=int, default=123, help='random seed')
    parser.add_argument('--lamda', type=int, default=100, help='L1 regularization factor')
    opt = parser.parse_args()

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    cudnn.benchmark = True

    torch.cuda.manual_seed(opt.seed)

    print('=> Loading datasets')

    # root directory voor google collab: "/content/drive/MyDrive/Thesis/DeepIllumination/dataset/"

    gt_name = opt.gt_name

    if opt.windows_filepaths:
        slash = "\\"
    else:
        slash = "/"

    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz).strftime('%d-%m-%Y_%Hh%Mm%Ss')
    writer = SummaryWriter("runs" + slash + opt.dataset + slash + now)

    root_dir = opt.dataset_directory
    if root_dir == "":
        root_dir = os.getcwd() + slash + "dataset" + slash

    train_dir = join(root_dir + opt.dataset, "train")
    test_dir = join(root_dir + opt.dataset, "val")

    train_set = DataLoaderHelper(train_dir, buffer_names, gt_name)
    val_set = DataLoaderHelper(test_dir, buffer_names, gt_name)

    batch_size = opt.train_batch_size
    n_epoch = opt.n_epoch

    train_data = DataLoader(dataset=train_set, num_workers=opt.workers, batch_size=opt.train_batch_size, shuffle=True)
    val_data = DataLoader(dataset=val_set, num_workers=opt.workers, batch_size=opt.test_batch_size, shuffle=False)

    print('=> Computing means & stds')

    (means, stds) = util.get_mean_and_std(train_data)

    print('=> Building model')

    netG = G(opt.n_channel_input * len(buffer_names), opt.n_channel_output, opt.n_generator_filters, means, stds, device)
    netG.apply(weights_init)
    netD = D(opt.n_channel_input * len(buffer_names), opt.n_channel_output, opt.n_discriminator_filters, means, stds, device)
    netD.apply(weights_init)

    criterion = nn.BCELoss()
    criterion_l1 = nn.L1Loss()

    buffers = []
    for i in range(0, len(buffer_names)):
        buffers.append(torch.FloatTensor(opt.train_batch_size, opt.n_channel_input, 256, 256))

    gt = torch.FloatTensor(opt.train_batch_size, opt.n_channel_output, 256, 256)

    label = torch.FloatTensor(opt.train_batch_size)
    real_label = 1
    fake_label = 0

    netD = netD.to(device)
    netG = netG.to(device)
    criterion = criterion.to(device)
    criterion_l1 = criterion_l1.to(device)

    for i in range(0, len(buffers)):
        buffers[i] = buffers[i].to(device)
    gt = gt.to(device)
    label = label.to(device)

    buffers = [Variable(buffer) for buffer in buffers]
    gt = Variable(gt)
    label = Variable(label)

    optimizerD = optim.Adam(netD.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
    optimizerG = optim.Adam(netG.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
    lastEpoch = 0

    if opt.resume_G:  # (bij het resumen worden de nieuwe means en stds gebruikt, deze worden niet heringeladen) #TODO resumen werkt miss ni meer nu mappen zijn aangepast
        if os.path.isfile(opt.resume_G):
            print("=> loading generator checkpoint '{}'".format(opt.resume_G))
            checkpoint = torch.load(opt.resume_G)
            lastEpoch = checkpoint['epoch']
            n_epoch = n_epoch - lastEpoch
            netG.load_state_dict(checkpoint['state_dict_G'])
            optimizerG.load_state_dict(checkpoint['optimizer_G'])
            print("=> loaded generator checkpoint '{}' (epoch {})".format(opt.resume_G, checkpoint['epoch']))

        else:
            print("=> no checkpoint found")

    if opt.resume_D:
        if os.path.isfile(opt.resume_D):
            print("=> loading discriminator checkpoint '{}'".format(opt.resume_D))
            checkpoint = torch.load(opt.resume_D)
            netD.load_state_dict(checkpoint['state_dict_D'])
            optimizerD.load_state_dict(checkpoint['optimizer_D'])
            print("=> loaded discriminator checkpoint '{}'".format(opt.resume_D))


    def train(epoch):
        full_running_loss = 0.0
        l1_running_loss = 0.0
        for (i, images) in enumerate(train_data):
            netD.zero_grad()
            with torch.no_grad():
                for j in range(0, len(buffers)):
                    buffers[j].resize_(images[j].size()).copy_(images[j])
                gt.resize_(images[-1].size()).copy_(images[-1])
            output = netD(torch.cat(buffers + [gt], 1))
            with torch.no_grad():
                label.resize_(output.size()).fill_(real_label)
            err_d_real = criterion(output, label)  # = fout op echt voorbeeld
            err_d_real.backward()
            d_x_y = output.data.mean()  # gemiddelde uitvoer voor elke patch
            fake_B = netG(torch.cat(buffers, 1))
            output = netD(torch.cat(buffers + [netG.unnormalize_gt(fake_B.detach())], 1))
            label.data.resize_(output.size()).fill_(fake_label)
            err_d_fake = criterion(output, label)  # = fout op fake voorbeeld
            err_d_fake.backward()
            d_x_gx = output.data.mean()  # gemiddelde uitvoer voor elke patch
            err_d = (err_d_real + err_d_fake) * 0.5  # gemiddelde van fout op fake en echt voorbeeld
            optimizerD.step()

            netG.zero_grad()
            output = netD(torch.cat(buffers + [netG.unnormalize_gt(fake_B)], 1))  # uitvoer voor elke patch van de discriminator voor dit gegenereerd sample
            label.data.resize_(output.size()).fill_(real_label)
            err_l1_g = criterion_l1(fake_B, netG.normalize_gt(gt))
            err_g = criterion(output, label) + opt.lamda \
                    * err_l1_g  # fout van generator voor dit voorbeeld
            err_g.backward()
            d_x_gx_2 = output.data.mean()  # gemiddelde uitvoer voor elke patch van de discriminator voor dit gegenereerd sample
            optimizerG.step()
            print('=> Epoch[{}]({}/{}): Loss_D: {:.4f} Loss_G: {:.4f} D(x): {:.4f} D(G(z)): {:.4f}/{:.4f}'.format(
                epoch,
                i,
                len(train_data),
                err_d.item(),
                err_g.item(),
                d_x_y,
                d_x_gx,
                d_x_gx_2,
            ))

            full_running_loss += err_g.item()
            l1_running_loss += err_l1_g.item()

            # log to tensorboard
            # if i % 5 == 4:
            #    writer.add_scalar('generator loss', running_loss / 5, epoch * len(train_data) + i)
            #    running_loss = 0.0

        writer.add_scalar('generator_full_loss/training', full_running_loss / len(train_data), epoch)
        writer.add_scalar('generator_l1_loss/training', l1_running_loss / len(train_data), epoch)


    def save_checkpoint(epoch):
        if not os.path.exists("checkpoint"):
            os.mkdir("checkpoint")
        if not os.path.exists(os.path.join("checkpoint", opt.dataset)):
            os.mkdir(os.path.join("checkpoint", opt.dataset))
        if not os.path.exists(os.path.join("checkpoint", opt.dataset, now)):
            os.mkdir(os.path.join("checkpoint", opt.dataset, now))
        net_g_model_out_path = "checkpoint" + slash + opt.dataset + slash + now + slash + "netG_model_epoch_{}.pth".format(epoch)
        net_d_model_out_path = "checkpoint" + slash + opt.dataset + slash + now + slash + "netD_model_epoch_{}.pth".format(epoch)
        torch.save({'epoch': epoch + 1, 'state_dict_G': netG.state_dict(), 'optimizer_G': optimizerG.state_dict(), 'norm_mean_G': means, 'norm_std_G': stds},
                   net_g_model_out_path)
        torch.save({'state_dict_D': netD.state_dict(), 'optimizer_D': optimizerD.state_dict()}, net_d_model_out_path) # TODO (slaagt means en stds ni op maar maakt ni echt uit)
        print("Checkpoint saved to {}".format("checkpoint" + opt.dataset))


    def validation(epoch):
        if opt.save_val_images:
            if not os.path.exists("validation"):
                os.mkdir("validation")
            if not os.path.exists(os.path.join("validation", opt.dataset)):
                os.mkdir(os.path.join("validation", opt.dataset))

        l1_running_loss = 0.0
        full_running_loss = 0.0
        mean_MSE_clamped = 0.0
        mean_SSIM_clamped = 0.0
        MSE = nn.MSELoss()
        kernel = gaussian_kernel(11, sigma=1.5).repeat(3, 1, 1).to(device)
        for index, images in enumerate(val_data):
            with torch.no_grad():
                for j in range(0, len(buffers)):
                    buffers[j].resize_(images[j].size()).copy_(images[j])
                gt.resize_(images[-1].size()).copy_(images[-1])
            out_G = netG(torch.cat(buffers, 1))

            out_D = netD(torch.cat(buffers + [netG.unnormalize_gt(out_G)], 1))
            with torch.no_grad():
                label.resize_(out_D.size()).fill_(real_label)
            err_l1_g = criterion_l1(out_G, netG.normalize_gt(gt))
            err_g = criterion(out_D, label) + opt.lamda * err_l1_g

            l1_running_loss += err_l1_g.item()
            full_running_loss += err_g.item()

            nn_result = netG.unnormalize_gt(out_G)

            nn_result[nn_result < 0] = 0

            # als het netwerk naar indirect optimaliseerd is gt alleen indirect
            if not gt_name == 'gt':
                direct_lighting = load_image(join(test_dir, "direct", val_set.image_filenames[index]))
                direct_lighting = direct_lighting[None, :].to(device)
                nn_result = torch.add(nn_result, direct_lighting)
                full_gi_gt = load_image(join(test_dir, "gt", val_set.image_filenames[index]))
                full_gi_gt = full_gi_gt[None, :].to(device)
                mean_MSE_clamped += MSE(nn_result, full_gi_gt).item()
                max = torch.max(torch.cat((nn_result, full_gi_gt), 1)).item()
                mean_SSIM_clamped += piqa.ssim.ssim(nn_result, full_gi_gt, kernel, value_range=max)[0].item()
            else:
                mean_MSE_clamped += MSE(nn_result, gt).item()
                max = torch.max(torch.cat((nn_result, gt), 1)).item()
                mean_SSIM_clamped += piqa.ssim.ssim(nn_result, gt, kernel, value_range=max)[0].item() #TODO max?

            if opt.save_val_images:
                if not os.path.exists("validation"):
                    os.mkdir("validation")
                if not os.path.exists(os.path.join("validation", opt.dataset)):
                    os.mkdir(os.path.join("validation", opt.dataset))
                if not os.path.exists(os.path.join("validation", opt.dataset, now)):
                    os.mkdir(os.path.join("validation", opt.dataset, now))
                out_img_normalized = nn_result.data[0]
                out_img = netG.unnormalize_gt(out_img_normalized).cpu()
                all_names = buffer_names + [gt_name]
                save_image(out_img, "validation/{}/{}_Fake.exr".format(opt.dataset + '/' + now, index))
                save_image(images[all_names.index(gt_name)][0], "validation/{}/{}_Real.exr".format(opt.dataset + '/' + now, index))
                save_image(images[all_names.index("direct")][0], "validation/{}/{}_Direct.exr".format(opt.dataset + '/' + now, index))
            # validation loss wordt niet berekend/gebruikt, alleen voor visuele confirmatie

        # log loss naar tensorboard (volledige loss/enkel l1 loss)
        writer.add_scalar('generator_full_loss/validation', full_running_loss / len(val_data), epoch)
        writer.add_scalar('generator_l1_loss/validation', l1_running_loss / len(val_data), epoch)
        writer.add_scalar('output_MSE/validation', mean_MSE_clamped / len(val_data), epoch)
        writer.add_scalar('output_SSIM/validation', mean_SSIM_clamped / len(val_data), epoch)


    for epoch in range(n_epoch):
        train(epoch + lastEpoch)
        if epoch % 1 == 0:  # TODO miss terug veranderen zodat steeds de laatste checkpoint wordt bijgehouden (trager maar ge kunt wel eerder stoppen)
            if opt.keep_every_checkpoint or epoch == opt.n_epoch - 1:
                save_checkpoint(epoch + lastEpoch)
            validation(epoch + lastEpoch)
        writer.close()
