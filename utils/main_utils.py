import natsort, glob, pickle, torch
import numpy as np
from IPython.core.display import display
from PIL import Image
from collections import OrderedDict
import options.options as option
from models import create_model
from utils.util import opt_get
import cv2
import os

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


def load_model(conf_path):
    opt = option.parse(conf_path, is_train=False)
    opt['gpu_ids'] = None
    opt = option.dict_to_nonedict(opt)
    model = create_model(opt)

    model_path = opt_get(opt, ['model_path'], None)
    model.load_network(load_path=model_path, network=model.netG)
    return model, opt


def predict(model, lr):
    model.feed_data({"LQ": t(lr)}, need_GT=False)
    model.test()
    visuals = model.get_current_visuals(need_GT=False)
    return visuals.get('rlt', visuals.get("SR"))


def imread(path):
    return cv2.imread(path)[:, :, [2, 1, 0]]


def imwrite(path, img):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img[:, :, [2, 1, 0]])


def imCropCenter(img, size):
    h, w, c = img.shape

    h_start = max(h // 2 - size // 2, 0)
    h_end = min(h_start + size, h)

    w_start = max(w // 2 - size // 2, 0)
    w_end = min(w_start + size, w)

    return img[h_start:h_end, w_start:w_end]


def impad(img, top=0, bottom=0, left=0, right=0, color=255):
    return np.pad(img, [(top, bottom), (left, right), (0, 0)], 'reflect')
