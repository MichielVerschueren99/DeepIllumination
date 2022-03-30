from os import listdir
from os.path import join

import torch.utils.data as data

from util import is_image, load_image


class DataLoaderHelper(data.Dataset):
    def __init__(self, image_dir, buffers, gt_name):
        super(DataLoaderHelper, self).__init__()
        buffer_paths = []
        for buffer in buffers:
            buffer_paths.append(join(image_dir, buffer))
        self.buffer_paths = buffer_paths
        self.gt_path = join(image_dir, gt_name)
        self.image_filenames = [x for x in listdir(self.buffer_paths[0]) if is_image(x)]


    def __getitem__(self, index):
        item = []
        for buffer_path in self.buffer_paths:
            item.append(load_image(join(buffer_path, self.image_filenames[index])))
        item.append(load_image(join(self.gt_path, self.image_filenames[index])))
        return item

    def __len__(self):
        return len(self.image_filenames)
