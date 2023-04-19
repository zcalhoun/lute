# Import all dependencies
import os
import torch
from multiprocessing import Pool
from torch.utils.data import Dataset


class MatchingDataset(Dataset):
    def __init__(self, file_path, files=None, transforms=None):
        self.file_path = file_path

        # Images
        if files is None:
            self.files = os.listdir(os.path.join(file_path, "img"))
        else:
            self.files = files

        # Define the number of processes to use
        self.num_processes = 8

    def __len__(self):
        return len(self.files)

    def _load_data(self, idx):
        img = torch.load(os.path.join(self.file_path, "img", self.files[idx]))

        with open(
            os.path.join(self.file_path, "labels", self.files[idx][:-3] + ".txt")
        ) as fp:
            label = float(fp.read())
        # Omit the tree class
        return img.numpy(), self.files[idx], label

    def __getitem__(self, idx):
        return self._load_data(idx)

    # Multiprocessing attempt
    def _load_data_parallel(self, indices):
        with Pool(self.num_processes) as p:
            data = p.map(self._load_data, indices)
        return data

    def get_data_parallel(self):
        indices = list(range(len(self)))
        return self._load_data_parallel(indices)
