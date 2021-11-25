Had to change the following files inside tensorflow library (see ./tf_changes):
 backend.py -- LOCAL_DEVICE XLA_GPU
 mult_gpu_model.py to support xla_gpu
