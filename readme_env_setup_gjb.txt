python setup on HPC:
 1. Activate Python 3 module
 2. setup conda (conda init)
 3. log out/log in
 4. create conda env with python 2.7.17 (e.g. conda create conda --name CAC27 python=2.7.17)
 5. conda activate CAC27
 6. conda install grpcio (b/c  pip is doesn't work for grpcio),
 7. install requirements using pip (e.g. pip install -r requirements.txt)
 9. update tensorflow code for xla_gpu support (see readme_gjb_changes_src.txt and /tf_changes directory)
