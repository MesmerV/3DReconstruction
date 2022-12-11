import sys, subprocess
import logging
import argparse


def ExecuteProcess(command:str, args:list=[], verbose=True):
    
    proc = subprocess.Popen(
        ([command]+args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
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

    parser.add_argument('Dataset_path', metavar='dataset_path', type=str, nargs=1,
                    help='The directory of your image dataset: see README.md to learn how to take good images')


    args = parser.parse_args()
    
    
    if len(sys.argv) < 2:
        logging.exception("Usage : python pipelineWindows.py dataSetPath")
        dataset_path = "./ImagesSets/Tests"
        
    else :
        dataset_path=sys.argv[1]  #Your dataset path

    print(40*"#","\n  Moving images in "+dataset_path,' into wrking dir:\n',40*"#")
    

    # image masks
    print(40*"#","\n  Processing images Masks\n",40*"#")

    # TODO separate two files and activate automatically the conda env
    
    ExecuteProcess("python",["utils.py"])
    
    res_path = "./MaskedResults"
    thr_value = 0.7
    #CreateMasks(dataset_path,result_path = res_path,thr_value = thr_value)