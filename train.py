import os
from os.path import join
import argparse
from math import log10

import torch
import torch.nn as nn
import torch.optim as optim
import torch.backends.cudnn as cudnn
import torchvision
from datetime import datetime

import util
from data import DataLoaderHelper
import pytz
from torch.utils.data import DataLoader
from torch.autograd import Variable
from model import G, D, weights_init
from util import load_image, save_image
from torch.utils.tensorboard import SummaryWriter

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DeepRendering-implemention')
    parser.add_argument('--dataset', required=True, help='output from unity')
    parser.add_argument('--dataset_directory', type=str, default="", help='give a custom dataset directory')
    parser.add_argument('--keep_every_checkpoint', type=bool, default=False,
                        help='keep the checkpoint that is generated after every epoch')
    parser.add_argument('--windows_filepaths', type=bool, default=False, help='use windows filepaths')
    parser.add_argument('--save_val_images', type=bool, default=False,
                        help='save the resulting images of the validation set')
    parser.add_argument('--train_batch_size', type=int, default=2, help='batch size for training')
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

    train_set = DataLoaderHelper(train_dir)
    val_set = DataLoaderHelper(test_dir)

    batch_size = opt.train_batch_size
    n_epoch = opt.n_epoch

    train_data = DataLoader(dataset=train_set, num_workers=opt.workers, batch_size=opt.train_batch_size, shuffle=True)
    val_data = DataLoader(dataset=val_set, num_workers=opt.workers, batch_size=opt.test_batch_size, shuffle=False)

    print('=> Computing means & stds')

    (means, stds) = util.get_mean_and_std(train_data)

    print('=> Building model')

    netG = G(opt.n_channel_input * 4, opt.n_channel_output, opt.n_generator_filters, means, stds, device)
    netG.apply(weights_init)
    netD = D(opt.n_channel_input * 4, opt.n_channel_output, opt.n_discriminator_filters)
    netD.apply(weights_init)

    criterion = nn.BCELoss()
    criterion_l1 = nn.L1Loss()

    albedo = torch.FloatTensor(opt.train_batch_size, opt.n_channel_input, 256, 256)
    direct = torch.FloatTensor(opt.train_batch_size, opt.n_channel_input, 256, 256)
    normal = torch.FloatTensor(opt.train_batch_size, opt.n_channel_input, 256, 256)
    depth = torch.FloatTensor(opt.train_batch_size, opt.n_channel_input, 256, 256)

    gt = torch.FloatTensor(opt.train_batch_size, opt.n_channel_output, 256, 256)

    label = torch.FloatTensor(opt.train_batch_size)
    real_label = 1
    fake_label = 0

    netD = netD.to(device)
    netG = netG.to(device)
    criterion = criterion.to(device)
    criterion_l1 = criterion_l1.to(device)

    albedo = albedo.to(device)
    direct = direct.to(device)
    normal = normal.to(device)
    depth = depth.to(device)
    gt = gt.to(device)
    label = label.to(device)

    albedo = Variable(albedo)
    direct = Variable(direct)
    normal = Variable(normal)
    depth = Variable(depth)
    gt = Variable(gt)
    label = Variable(label)

    optimizerD = optim.Adam(netD.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
    optimizerG = optim.Adam(netG.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
    lastEpoch = 0

    if opt.resume_G:  # (bij het resumen worden de nieuwe means en stds gebruikt, deze worden niet heringeladen)
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
            (albedo_cpu, direct_cpu, normal_cpu, depth_cpu, gt_cpu) = (
            images[0], images[1], images[2], images[3], images[4])

            with torch.no_grad():
                albedo.resize_(albedo_cpu.size()).copy_(albedo_cpu)
                direct.resize_(direct_cpu.size()).copy_(direct_cpu)
                normal.resize_(normal_cpu.size()).copy_(normal_cpu)
                depth.resize_(depth_cpu.size()).copy_(depth_cpu)
                gt.resize_(gt_cpu.size()).copy_(gt_cpu)
            output = netD(torch.cat((albedo, direct, normal, depth, gt), 1))
            with torch.no_grad():
                label.resize_(output.size()).fill_(real_label)
            err_d_real = criterion(output, label)  # = fout op echt voorbeeld
            err_d_real.backward()
            d_x_y = output.data.mean()  # gemiddelde uitvoer voor elke patch
            fake_B = netG(torch.cat((albedo, direct, normal, depth), 1))
            output = netD(torch.cat((albedo, direct, normal, depth, fake_B.detach()), 1))
            label.data.resize_(output.size()).fill_(fake_label)
            err_d_fake = criterion(output, label)  # = fout op fake voorbeeld
            err_d_fake.backward()
            d_x_gx = output.data.mean()  # gemiddelde uitvoer voor elke patch
            err_d = (err_d_real + err_d_fake) * 0.5  # gemiddelde van fout op fake en echt voorbeeld
            optimizerD.step()

            netG.zero_grad()
            output = netD(torch.cat((albedo, direct, normal, depth, fake_B),
                                    1))  # uitvoer voor elke patch van de discriminator voor dit gegenereerd sample
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
        net_g_model_out_path = "checkpoint" + slash + opt.dataset + slash + "netG_model_epoch_{}.pth".format(epoch)
        net_d_model_out_path = "checkpoint" + slash + opt.dataset + slash + "netD_model_epoch_{}.pth".format(epoch)
        torch.save({'epoch': epoch + 1, 'state_dict_G': netG.state_dict(), 'optimizer_G': optimizerG.state_dict(), 'norm_mean_G': means, 'norm_std_G': stds},
                   net_g_model_out_path)
        torch.save({'state_dict_D': netD.state_dict(), 'optimizer_D': optimizerD.state_dict()}, net_d_model_out_path)
        print("Checkpoint saved to {}".format("checkpoint" + opt.dataset))


    def validation(epoch):
        if opt.save_val_images:
            if not os.path.exists("validation"):
                os.mkdir("validation")
            if not os.path.exists(os.path.join("validation", opt.dataset)):
                os.mkdir(os.path.join("validation", opt.dataset))

        l1_running_loss = 0.0
        full_running_loss = 0.0
        for index, images in enumerate(val_data):
            (albedo_cpu, direct_cpu, normal_cpu, depth_cpu, gt_cpu) = (
            images[0], images[1], images[2], images[3], images[4])
            with torch.no_grad():
                albedo.resize_(albedo_cpu.size()).copy_(albedo_cpu)
                direct.resize_(direct_cpu.size()).copy_(direct_cpu)
                normal.resize_(normal_cpu.size()).copy_(normal_cpu)
                depth.resize_(depth_cpu.size()).copy_(depth_cpu)
                gt.resize_(gt_cpu.size()).copy_(gt_cpu)
            out_G = netG(torch.cat((albedo, direct, normal, depth), 1))

            out_D = netD(torch.cat((albedo, direct, normal, depth, out_G), 1))
            with torch.no_grad():
                label.resize_(out_D.size()).fill_(real_label)
            err_l1_g = criterion_l1(out_G, netG.normalize_gt(gt))
            err_g = criterion(out_D, label) + opt.lamda * err_l1_g

            l1_running_loss += err_l1_g.item()
            full_running_loss += err_g.item()

            if opt.save_val_images:
                out_G = out_G.cpu()
                out_img_normalized = out_G.data[0]
                out_img = netG.unnormalize_gt(out_img_normalized)
                save_image(out_img, "validation/{}/{}_Fake.exr".format(opt.dataset, index))
                save_image(gt_cpu[0], "validation/{}/{}_Real.exr".format(opt.dataset, index))
                save_image(direct_cpu[0], "validation/{}/{}_Direct.exr".format(opt.dataset, index))
            # validation loss wordt niet berekend/gebruikt, alleen voor visuele confirmatie

        # log loss naar tensorboard (volledige loss/enkel l1 loss)
        writer.add_scalar('generator_full_loss/validation', full_running_loss / len(val_data), epoch)
        writer.add_scalar('generator_l1_loss/validation', l1_running_loss / len(val_data), epoch)


    for epoch in range(n_epoch):
        train(epoch + lastEpoch)
        if epoch % 1 == 0:  # TODO miss terug veranderen zodat steeds de laatste checkpoint wordt bijgehouden (trager maar ge kunt wel eerder stoppen)
            if opt.keep_every_checkpoint or epoch == opt.n_epoch - 1:
                save_checkpoint(epoch + lastEpoch)
            validation(epoch + lastEpoch)
        writer.close()
