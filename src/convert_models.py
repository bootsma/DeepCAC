from step1_heartloc import heartloc_model
from step2_heartseg import heartseg_model
from step3_cacseg import cacseg_model
import yaml
import argparse

version=1
def init_args():
    parser = argparse.ArgumentParser(description="convert_models.py \n"
                                                 f" Version: {version}\n"
                                                 " Author: Gregory J. Bootsma, Copyright 2023\n"
                                                 " Description:\n\t"
                                                 "Takes a config yaml associated with one of the Deep-CAC steps and converts the multi-gpu model to a single gpu model.")

    parser.add_argument('yaml_file', type=str, help="path to yaml config file ")
    parser.add_argument('step_number', type=int, help='The step number (1,2,or3) the model is associated with')
    return parser.parse_args()

def convert_step1_multi_gpu_model_2_single( config_yaml ):
    """
    Converts a multi gpu model to single gpu, get around a bug in older version of TF
    """
    print('Converting step 1 model using config {}'.format(config_yaml))
    with open(config_yaml) as f:
        yaml_conf = yaml.load(f, Loader=yaml.FullLoader)

    data_folder_path = os.path.normpath(yaml_conf["io"]["path_to_data_folder"])
    heartloc_data_folder_name = yaml_conf["io"]["heartloc_data_folder_name"]
    weights_file_name = yaml_conf["model"]["weights_file_name"]
    model_weights_folder_name = yaml_conf["io"]["model_weights_folder_name"]
    heartloc_data_path = os.path.join(data_folder_path, heartloc_data_folder_name)
    model_weights_dir_path = os.path.join(heartloc_data_path, model_weights_folder_name)
    weights_file = os.path.join(model_weights_dir_path, weights_file_name)
    assert os.path.exists(weights_file)


    print("Loading saved model from {}".format(weights_file))

    extended = yaml_conf["model"]["extended"]
    down_steps = yaml_conf["model"]["down_steps"]
    crop_size= yaml_conf["processing"]["model_input_size"]


    """
    This needs 2 gpus minimum to convert
    """
    input_shape = (crop_size, crop_size, crop_size, 1)
    model = heartloc_model.get_unet_3d(down_steps=down_steps, input_shape=input_shape, mgpu=2, ext=extended)
    model.load_weights(weights_file)

    single_gpu_model = model.layers[-2]
    tmp_weights_file = weights_file[:weights_file.rfind('.')] + '_single_gpu.h5'
    print('Saving single gpu model weights as {}'.format(tmp_weights_file))
    single_gpu_model.save_weights(tmp_weights_file)
    print('Finished model `')

def convert_step2_multi_gpu_model_2_single( config_yaml ):
    """
    Converts a multi gpu model to single gpu, get around a bug in older version of TF
    """
    print('Converting step 2 model using config {}'.format(config_yaml))
    with open(config_yaml) as f:
        yaml_conf = yaml.load(f, Loader=yaml.FullLoader)

    data_folder_path = os.path.normpath(yaml_conf["io"]["path_to_data_folder"])
    heartloc_data_folder_name = yaml_conf["io"]["heartloc_data_folder_name"]
    weights_file_name = yaml_conf["model"]["weights_file_name"]
    model_weights_folder_name = yaml_conf["io"]["model_weights_folder_name"]
    heartloc_data_path = os.path.join(data_folder_path, heartloc_data_folder_name)
    model_weights_dir_path = os.path.join(heartloc_data_path, model_weights_folder_name)
    weights_file = os.path.join(model_weights_dir_path, weights_file_name)
    assert os.path.exists(weights_file)


    print("Loading saved model from {}".format(weights_file))

    extended = yaml_conf["model"]["extended"]
    down_steps = yaml_conf["model"]["down_steps"]
    training_size = yaml_conf["processing"]["training_size"]


    """
    This needs 2 gpus minimum to convert
    """
    input_shape = (training_size[2], training_size[1], training_size[0], 1)
    model = heartseg_model.get_unet_3d(down_steps=down_steps, input_shape=input_shape, mgpu=2, ext=True)
    model.load_weights(weights_file)

    single_gpu_model = model.layers[-2]
    tmp_weights_file = weights_file[:weights_file.rfind('.')] + '_single_gpu.h5'
    print('Saving single gpu model weights as {}'.format(tmp_weights_file))
    single_gpu_model.save_weights(tmp_weights_file)
    print('Finished model 2')

def convert_step3_multi_gpu_model_2_single( config_yaml ):
    """
    Converts a multi gpu model to single gpu, get around a bug in older version of TF
    """
    print('Converting step 3 model using config {}'.format(config_yaml))
    with open(config_yaml) as f:
        yaml_conf = yaml.load(f, Loader=yaml.FullLoader)

    data_folder_path = os.path.normpath(yaml_conf["io"]["path_to_data_folder"])
    heartloc_data_folder_name = yaml_conf["io"]["heartloc_data_folder_name"]
    weights_file_name = yaml_conf["model"]["weights_file_name"]
    model_weights_folder_name = yaml_conf["io"]["model_weights_folder_name"]
    heartloc_data_path = os.path.join(data_folder_path, heartloc_data_folder_name)
    model_weights_dir_path = os.path.join(heartloc_data_path, model_weights_folder_name)
    weights_file = os.path.join(model_weights_dir_path, weights_file_name)
    assert os.path.exists(weights_file)


    print("Loading saved model from {}".format(weights_file))


    """
    This needs 2 gpus minimum to convert
    """

    #3rd model seems to be all hardcoded in step3

    pool_size = (2, 2, 2)
    conv_size = (3, 3, 3)
    cube_size = [64, 64, 32]
    input_shape = (cube_size[2], cube_size[1], cube_size[0], 1)
    optimizer = 'ADAM'
    extended = True
    drop_out = 0.5
    down_steps = 3

    model = cacseg_model.getUnet3d(down_steps=down_steps, input_shape=input_shape, pool_size=pool_size,
                                   conv_size=conv_size, initial_learning_rate=lr, mgpu=2,
                                   extended=extended, drop_out=drop_out, optimizer=optimizer)
    model.load_weights(weights_file)

    single_gpu_model = model.layers[-2]
    tmp_weights_file = weights_file[:weights_file.rfind('.')] + '_single_gpu.h5'
    print('Saving single gpu model weights as {}'.format(tmp_weights_file))
    single_gpu_model.save_weights(tmp_weights_file)

    print('Finished model 3')