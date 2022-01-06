from utils.main_utils import *
from Measure import Measure, psnr
from collections import OrderedDict
from imresize import imresize
# Global config
conf_path = './confs/SRFlow_CelebA_8X.yml'
test_lr_path = './data/validation/lr/001.png'
test_gt_path = './data/validation/gt/001.png'


def superResolve(model, opt, conf, lr_path, gt_path, sr_path, heat, measure, pad_factor=2):
    lr = imread(lr_path)
    gt = imread(gt_path)

    scale = opt['scale']
    h, w, c = lr.shape
    lq_orig = lr.copy()
    lr = impad(lr, bottom=int(np.ceil(h / pad_factor) * pad_factor - h),
               right=int(np.ceil(w / pad_factor) * pad_factor - w))

    lr_t = t(lr)  # torch tensor
    if heat is None:
        heat = opt['heat']

    sr_t = model.get_sr(lq=lr_t, heat=heat)

    sr = rgb(torch.clamp(sr_t, 0, 1))
    sr = sr[:h * scale, :w * scale]
    meas = OrderedDict(conf=conf, heat=heat, name=0)
    meas['PSNR'], meas['SSIM'], meas['LPIPS'] = measure.measure(sr, gt)
    lr_reconstruct_rgb = imresize(sr, 1 / opt['scale'])
    meas['LRC PSNR'] = psnr(lq_orig, lr_reconstruct_rgb)
    str_out = format_measurements(meas)
    print(str_out)
    if sr_path is not None:
        imwrite(sr_path, sr)

def main():
    model, opt = load_model(conf_path)
    conf = conf_path.split('/')[-1].replace('.yml', '')
    lr_dir = opt['dataroot_LR']
    gt_dir = opt['dataroot_GT']
    sr_dir = opt['dataroot_SR'] # the output directory
    measure = Measure(use_gpu=False)
    this_dir = os.path.dirname(os.path.realpath(__file__))
    test_lr_path = os.path.join(this_dir,lr_dir,'000001.jpg')
    test_gt_path = os.path.join(this_dir, gt_dir, '000001.jpg')
    output_path = os.path.join(this_dir,sr_dir, '000001.jpg')
    lr = imread(test_lr_path)
    gt = imread(test_gt_path)

    scale = opt['scale']
    pad_factor = 2
    h, w, c = lr.shape
    lq_orig = lr.copy()
    lr = impad(lr, bottom=int(np.ceil(h / pad_factor) * pad_factor - h),
               right=int(np.ceil(w / pad_factor) * pad_factor - w))

    lr_t = t(lr) # torch tensor
    heat = opt['heat']
    sr_t = model.get_sr(lq=lr_t, heat=heat)

    sr = rgb(torch.clamp(sr_t, 0, 1))
    sr = sr[:h * scale, :w * scale]
    meas = OrderedDict(conf=conf, heat=heat, name=0)
    meas['PSNR'], meas['SSIM'], meas['LPIPS'] = measure.measure(sr, gt)
    lr_reconstruct_rgb = imresize(sr, 1 / opt['scale'])
    meas['LRC PSNR'] = psnr(lq_orig, lr_reconstruct_rgb)


    str_out = format_measurements(meas)
    imwrite(output_path, sr)
    print(str_out)

if __name__ == '__main__':
    main()
