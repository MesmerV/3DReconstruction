"""
Requirements :
Python >= 3.7,
Pytorch entre 1.8 et 1.10 et version de torchvision compatible(ex: Pytorch 1.10.0 et torchvision 0.11.1),
OpenCV,
Pip,
Detectron2 : Exécuter le script suivant dans le terminal:
    python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
"""
import torch, detectron2
TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
print("detectron2:", detectron2.__version__)

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

import numpy as np
import os, json, cv2, random

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

cfg = get_cfg()
cfg.MODEL.DEVICE = "cpu"
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)


def removePersons(img):
    outputs = predictor(img)
    print('Analyzed')
    print(outputs["instances"].pred_classes)
    for n in range(outputs["instances"].pred_masks.numpy().shape[0]):
        mask = outputs["instances"].pred_masks.numpy()[n]
        classe = outputs["instances"].pred_classes.numpy()[n]
        if (classe != 0 and classe < 30):
            for x in range(mask.shape[0]):
                for y in range(mask.shape[1]):
                    if (mask[x][y] == True) :
                        img[x][y] = [0, 0, 0]
    return img
srcPath = "./pathOfThePictiresDir/"
outPath = "./pathOfTheOutputDir/"
for file in os.listdir(srcPath) :
    im = cv2.imread(srcPath + file)
    im2 = removePersons(im)
    cv2.imwrite(outPath + file, im2)
print("Over")