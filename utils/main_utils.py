import natsort, glob, pickle, torch
import numpy as np
from IPython.core.display import display
from PIL import Image
from collections import OrderedDict

def find_files(wildcard):
    """
    Find the files that fit the wildcard description
    :param wildcard: a query string
    :return: a list of files found
    """
    return natsort.natsorted(glob.glob(wildcard, recursive=True))


def imshow(array):
    """
    Display the image given in the array
    :param array: the image
    :return:
    """
    display(Image.fromarray(array))


def pickleRead(path):
    """
    Read a pickle file and load the python object
    :param path: path to the pickle file
    :return: the python object
    """
    with open(path, 'rb') as f:
        return pickle.load(f)


def t(array):
    """
    Convert rgb image array to tensor
    :param array: RGB image
    :return: float32 torch.Tensor object
    """
    return torch.Tensor(np.expand_dims(array.transpose([2, 0, 1]), axis=0).astype(np.float32)) / 255


def rgb(t):
    """
    Convert torch.Tensor object to RGB image
    :param t: torch.Tensor object
    :return: RGB image numpy array
    """
    return (np.clip((t[0] if len(t.shape) == 4 else t).detach().cpu().numpy().transpose([1, 2, 0]), 0, 1) * 255).astype(np.uint8)