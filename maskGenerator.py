import os, sys, argparse
import time
import numpy as np
from skimage import io
import time
from glob import glob
from tqdm import tqdm

import torch, gc
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import torch.nn.functional as F
from torchvision.transforms.functional import normalize

import requests

sys.path.append("DIS/IS-Net")

from models import *


def CreateMasks(dataset_path,result_path,thr=0,write_masked=False):
    model_path="DIS/saved_models/IS-Net/isnet-general-use.pth"  # the model path
    input_size=[1024,1024]
    net=ISNetDIS()

    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_path))
        net=net.cuda()
    else:
        net.load_state_dict(torch.load(model_path,map_location="cpu"))
    net.eval()
    im_list = glob(dataset_path+"/*.jpg")+glob(dataset_path+"/*.JPG")+glob(dataset_path+"/*.jpeg")+glob(dataset_path+"/*.JPEG")+glob(dataset_path+"/*.png")+glob(dataset_path+"/*.PNG")+glob(dataset_path+"/*.bmp")+glob(dataset_path+"/*.BMP")+glob(dataset_path+"/*.tiff")+glob(dataset_path+"/*.TIFF")


    for i, im_path in tqdm(enumerate(im_list), total=len(im_list)):
        print("im_path: ", im_path)
        im = io.imread(im_path)
        if len(im.shape) < 3:
            im = im[:, :, np.newaxis]
        im_shp=im.shape[0:2]
        im_tensor = torch.tensor(np.copy(im), dtype=torch.float32).permute(2,0,1)
        im_tensor = F.upsample(torch.unsqueeze(im_tensor,0), input_size, mode="bilinear").type(torch.uint8)
        image = torch.divide(im_tensor,255.0)
        image = normalize(image,[0.5,0.5,0.5],[1.0,1.0,1.0])

        if torch.cuda.is_available():
            image=image.cuda()
        result=net(image)
        result=torch.squeeze(F.upsample(result[0][0],im_shp,mode='bilinear'),0)
        ma = torch.max(result)
        mi = torch.min(result)
        result = (result-mi)/(ma-mi)

        im_name=os.path.basename(im_path).split('.')[0]
        mask = (result*255).permute(1,2,0).cpu().data.numpy().astype(np.uint8)

        #if thr then write binary images
        if thr:
            masq = 255*(mask > 255*thr).astype(np.uint8)
            io.imsave(os.path.join(result_path,im_name+"_Masq.tif"),masq)
        else:
            io.imsave(os.path.join(result_path,im_name+"_Masq.tif"),mask)

    return


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Contouring tool that compute images masks using DIS DCNN from Highly Accurate Dichotomous Image Segmentation （ECCV 2022）](https://arxiv.org/pdf/2203.03041.pdf)')

    parser.add_argument('dataset_path', metavar='dataset_path', type=str,
                    help='The directory of your image dataset: see README.md to learn how to take good images')
    parser.add_argument('result_path', metavar='result_path', type=str,
                    help='The directory where masqs will be written')


    args = parser.parse_args()


    CreateMasks(args.dataset_path,args.result_path,thr=0)
    
