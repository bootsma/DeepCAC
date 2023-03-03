Had to change the following files inside tensorflow library (see ./tf_changes):
 backend.py -- LOCAL_DEVICE XLA_GPU
 multi_gpu_model.py to support xla_gpu
 
To find location of TensorFlow files:
  1. Open python console (python)
  2. Import tensorflow (import tensorflow as tf)
  3. Print location of file (print(tf.__file__) (e.g. <SOMEDIR>/site-packages/tensorflow/__init__.pyc, tensorflow dir TENSOR_DIR=<SOMEDIR>/site-packages/tensorflow)
  4. backend.py should be located in $TENSOR_DIR/python/keras
     4.1 move original (mv $TENSOR_DIR/python/keras/backend.py $TENSOR_DIR/python/keras/backend.py.old)
     4.2 copy new (cp 
  5. mult_
  
