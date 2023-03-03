python setup on HPC:
 1. Setup Conda:
     1.1 Method 1:
        1.1.1 Activate Python 3 module (module load python3)
        1.1.2 setup conda (conda init)
        1.1.3. log out/log in
     1.2 Method 2:
        1.2.1 Download and install Anaconda (ee https://www.anaconda.com/products/distribution#linux)
 4. Create conda env with python 2.7.17 (e.g. conda --name cac27 python=2.7.17)
 5. Activate your new env (e.g. conda activate cac27)
 6. Use conda to install grpcio (b/c  pip is doesn't work for grpcio, e.g.  conda install -c anaconda grpcio)
 7. Download and install DeepCAC (e.g. git clone https://github.com/bootsma/)
 8. install requirements using pip (e.g. pip install -r requirements.txt)
 9. update tensorflow code for xla_gpu support (see readme_gjb_changes_src.txt and /tf_changes directory)
