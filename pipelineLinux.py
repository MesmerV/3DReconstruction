import os, sys, subprocess
import logging
import argparse

from maskGenerator import CreateMasks

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
    return


if __name__=="__main__":
    
    parser = argparse.ArgumentParser(
        description='Photogrammetry Pipeline developped as an INF557 project')
    parser.add_argument('dataset_path', metavar='dataset_path', type=str,
                    help='The directory of your image dataset: see README.md to learn how to take good images')

    args = parser.parse_args()
    
    # Create workspace for MicMac with copies of images
    print(40*"#","\n  Cleaning workspace ...\n" + 40*"#")
    ExecuteProcess("rm -r workspace",shell=True)
    ExecuteProcess("mkdir workspace",shell=True)

    print(40*"#","\n  Copying images in "+args.dataset_path,' into wrking dir:\n' + 40*"#")
    ExecuteProcess("cp",[args.dataset_path +"*.jpg","workspace"],shell=True)

    # Create image masks
    print(40*"#","\n  Processing images Masks\n"+40*"#")
    #CreateMasks("workspace","workspace",thr=0.5 ,write_masked=False)

    #Change working directory
    os.chdir("./workspace")

    # Run Tapioca to find tie points
    ExecuteProcess("mm3d",["Tapioca","MulScale",".*jpg","800","2500"])

    #Schnaps that gets the points

    ExecuteProcess("mm3d",["Tapas","Fraser",".*jpg","Out=Projet"])

    # homolFilterPoints

    # C3DC

    #TiPunch

    #Save mesh !