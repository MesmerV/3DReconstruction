import os, sys, subprocess
import logging
import argparse
from glob import glob
from skimage import io
from maskGenerator import CreateMasks
import time

#function that execute a process and print its stdout live
def ExecuteProcess(command:str, args:list=[], shell=False, verbose=True):
    if shell:
        cmd = command
        for arg in args:
            cmd += " " + arg
    else:
        cmd = [command]+ args
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=shell
        )
    
    #Catch KeyBoard interrupt

    try:
        line = None
        while line or proc.poll() is None:
            line = proc.stdout.readline()
            print(line.replace('\n',''))

    except KeyboardInterrupt:
        proc.terminate()
        
    out, err = proc.communicate()
    print(out)
    print(err)

    return proc.returncode

def GetImagesList(dataset_path):
    im_list = glob(dataset_path+"/*.jpg")+glob(dataset_path+"/*.JPG")+glob(dataset_path+"/*.jpeg")+glob(dataset_path+"/*.JPEG")+glob(dataset_path+"/*.png")+glob(dataset_path+"/*.PNG")+glob(dataset_path+"/*.bmp")+glob(dataset_path+"/*.BMP")+glob(dataset_path+"/*.tiff")+glob(dataset_path+"/*.TIFF")
    return im_list

def printTitle(title):
    sep = 2*(100*"#"+'\n')
    print('\n' + sep + '\n\t\t' + title + '\n\n' + sep + 2*'\n')

def MicMacPipeline(args,img):
    """ Implement a fully automated Photogrammetry pipeline with extra tools to help digitalizing your stuff !"""

    #define matcher for image detection
    matcher = ".*"+args.imgType

    im_shp=img.shape[0:2]
    img_def = min(im_shp)

    first_scale  = int(img_def/6)
    second_scale  = int(img_def/1.9)
    
    ################################################################################################   
    ################################################ MICMAC PIPELINE ###############################
    ################################################################################################
    
    # Run Tapioca to find tie points
    printTitle("Run Tapioca Mulscale " + str(first_scale) + ' ' + str(second_scale)+" - Find Tie Points")
    time.sleep(5)
    if ExecuteProcess("mm3d",["Tapioca","MulScale",matcher,str(first_scale),str(second_scale)]):
        return


    #Schnaps that gets the points
    printTitle("Run Schnaps - checks tie points quality")
    ExecuteProcess("mm3d",["Schnaps",matcher,"MoveBadImgs=true","NbWin=100"])
    

    #Tapas finds the camera positions
    printTitle("Run Tapas - Optimize camera pos")
    if ExecuteProcess("mm3d",["Tapas","RadialExtended",matcher,"Out=Projet"]):
        return

    # homolFilterPoints
    printTitle("Run HomolFilterMasq - Filter tie points")
    if ExecuteProcess("mm3d",["HomolFilterMasq",matcher,"ANM=true"]):
        return

    # C3DC
    printTitle("Run C3DC - Create a Dense Point Cloud")
    if ExecuteProcess("mm3d",["C3DC","MicMac",matcher,"Projet","SH=MasqFiltered"]):
        return

    #TiPunch


    #Save mesh !
    return 


if __name__=="__main__":

    # Parse arguments and prints usage if needed
    
    parser = argparse.ArgumentParser(
        description='Photogrammetry Pipeline developped as an INF557 project')
    parser.add_argument('dataset_path', metavar='dataset_path', type=str,
                    help='The directory of your image dataset: see README.md to learn how to take good images')
    parser.add_argument('--with_masks', action='store_true')
    args = parser.parse_args()

    #TODO check if steps are already done or not -> can restart not from the begining ! 

    # Create workspace for MicMac with copies of images
    printTitle( "Cleaning workspace ...")
    ExecuteProcess("rm -r workspace",shell=True)
    ExecuteProcess("mkdir workspace",shell=True)

    # Look for images in dataset folder
    im_list = GetImagesList(args.dataset_path)
    args.imgType = im_list[0].split('.')[-1]
    print("\n Found ",len(im_list), " images of type ",args.imgType,"\n\n" )

    first_im = io.imread(im_list[0])
    
    printTitle("Copying images in "+args.dataset_path+" into wrking dir:")
    ExecuteProcess("cp",[args.dataset_path +"/*."+args.imgType,"workspace"],shell=True)
        
    if args.with_masks:
        # Create image masks
        printTitle("Processing images Masks")
        CreateMasks("workspace","workspace",thr=0.1 ,write_masked=False)

    #Change working directory
    os.chdir("./workspace")    
    
    #launch pieline with args
    MicMacPipeline(args, first_im)
    