"""
  ----------------------------------------
    HeartLoc - run DeepCAC pipeline step1
  ----------------------------------------
  ----------------------------------------
  Author: AIM Harvard
  
  Python Version: 2.7.17
  ----------------------------------------
  
  Deep-learning-based heart localization
  in Chest CT scans - all param.s are read
  from a config file stored under "/config"
  
"""

import os
import yaml
import argparse
import matplotlib      
matplotlib.use('Agg')

from step1_heartloc import export_data, downsample_data, input_data_prep, run_inference, upsample_results

## ----------------------------------------

base_conf_file_path = 'config/'
conf_file_list = [f for f in os.listdir(base_conf_file_path) if f.split('.')[-1] == 'yaml']

parser = argparse.ArgumentParser(description = 'Run pipeline step 1 - heart localization.')

parser.add_argument('--conf',
                    required = False,
                    help = 'Specify the YAML configuration file containing the run details. ' \
                            + 'Defaults to "step1_heart_localization.yaml"',
                    choices = conf_file_list,
                    default = "step1_heart_localization.yaml",
                   )


args = parser.parse_args()

print('Running Config File: {}'.format(args.conf))
conf_file_path = os.path.join(base_conf_file_path, args.conf)

with open(conf_file_path) as f:
  yaml_conf = yaml.load(f, Loader = yaml.FullLoader)


# input-output
data_folder_path = os.path.normpath(yaml_conf["io"]["path_to_data_folder"])

raw_data_folder_name = yaml_conf["io"]["raw_data_folder_name"]

# GJB 2021, add method for grabbing and processing h5 data from one folder
# for h5 all data is in one folder and only data in a csv file is process
# you can either explicitly list csv file or put only one csv file in the data
# folder
raw_data_proc_type = yaml_conf["io"].get("raw_data_proc_type")
raw_data_patient_csv_file = yaml_conf["io"].get("patient_csv_file")


###########################################################
# VOXEL SPACING and ORIENTATION SETTINGS
#voxel information can either be taken from csv file or h5 data, only matters if raw_data_proc_type == "h5_one_dir"
raw_data_h5_voxel_info = yaml_conf["io"].get("raw_data_h5_voxel_info", False)
spacing_assignment = yaml_conf["io"].get("assign_patient_mask_spacing",0)

heartloc_data_folder_name = yaml_conf["io"]["heartloc_data_folder_name"]

curated_data_folder_name = yaml_conf["io"]["curated_data_folder_name"]
qc_curated_data_folder_name = yaml_conf["io"]["qc_curated_data_folder_name"]
resampled_data_folder_name = yaml_conf["io"]["resampled_data_folder_name"]
model_input_folder_name = yaml_conf["io"]["model_input_folder_name"]
model_weights_folder_name = yaml_conf["io"]["model_weights_folder_name"]
model_output_folder_name = yaml_conf["io"]["model_output_folder_name"]
upsampled_data_folder_name = yaml_conf["io"]["upsampled_data_folder_name"]

# preprocessing and inference parameters
has_manual_seg = yaml_conf["processing"]["has_manual_seg"]
fill_mask_holes = yaml_conf["processing"]["fill_mask_holes"]
export_png = yaml_conf["processing"]["export_png"]
num_cores = yaml_conf["processing"]["num_cores"]
create_test_set = yaml_conf["processing"]["create_test_set"]
curated_size = yaml_conf["processing"]["curated_size"]
curated_spacing = yaml_conf["processing"]["curated_spacing"]
model_input_size = yaml_conf["processing"]["model_input_size"]
model_input_spacing = yaml_conf["processing"]["model_input_spacing"]

# number of gpus to use, 4 should be used for training
number_of_gpus = yaml_conf["processing"].get("number_of_gpus", 4)

# model config
weights_file_name = yaml_conf["model"]["weights_file_name"]
down_steps = yaml_conf["model"]["down_steps"]
extended = yaml_conf["model"]["extended"]



## ----------------------------------------

raw_data_dir_path = os.path.join(data_folder_path, raw_data_folder_name)

# set paths: pre-processing, curation and resampling
heartloc_data_path = os.path.join(data_folder_path, heartloc_data_folder_name)
curated_dir_path = os.path.join(heartloc_data_path, curated_data_folder_name)
qc_curated_dir_path = os.path.join(heartloc_data_path, qc_curated_data_folder_name)
resampled_dir_path = os.path.join(heartloc_data_path, resampled_data_folder_name)

# set paths: model processing
model_input_dir_path = os.path.join(heartloc_data_path, model_input_folder_name)
model_weights_dir_path = os.path.join(heartloc_data_path, model_weights_folder_name)
model_output_dir_path = os.path.join(heartloc_data_path, model_output_folder_name)

# set paths: final location of the inferred masks (NRRD)
model_output_nrrd_dir_path = os.path.join(heartloc_data_path, upsampled_data_folder_name)


# create the subfolders where the results are going to be stored
if not os.path.exists(curated_dir_path): os.makedirs(curated_dir_path)
if not os.path.exists(qc_curated_dir_path): os.mkdir(qc_curated_dir_path)
if not os.path.exists(resampled_dir_path): os.mkdir(resampled_dir_path)
if not os.path.exists(model_input_dir_path): os.mkdir(model_input_dir_path)

# assert the weights folder exists and the weights file is found
weights_file = os.path.join(model_weights_dir_path, weights_file_name)
assert os.path.exists(weights_file)

if not os.path.exists(model_output_dir_path): os.mkdir(model_output_dir_path)
if not os.path.exists(model_output_nrrd_dir_path): os.mkdir(model_output_nrrd_dir_path)

## ----------------------------------------

# run the localization pipeline
print "\n--- STEP 1 - HEART LOCALIZATION ---\n"

# data preparation
if raw_data_proc_type is None:
    export_data.export_data(raw_data_dir_path = raw_data_dir_path,
                        curated_dir_path = curated_dir_path,
                        qc_curated_dir_path = qc_curated_dir_path,
                        curated_size = curated_size,
                        curated_spacing = curated_spacing,
                        num_cores = num_cores,
                        export_png = export_png,
                        has_manual_seg = has_manual_seg)
elif raw_data_proc_type == "h5_one_dir":
    print( "CSV File: {}".format(raw_data_patient_csv_file))
    export_data.export_data_h5(raw_data_dir_path=raw_data_dir_path,
                            curated_dir_path=curated_dir_path,
                            qc_curated_dir_path=qc_curated_dir_path,
                            curated_size=curated_size,
                            curated_spacing=curated_spacing,
                            num_cores=num_cores,
                            export_png=export_png,
                            has_manual_seg=has_manual_seg,
                            patient_csv_file=raw_data_patient_csv_file,
                            patient_h5_voxel_info=raw_data_h5_voxel_info,
                            spacing_assignment =spacing_assignment
                            )
else:
    raise Exception("Unkown raw data process type: {}".format(raw_data_proc_type))
# data downsampling
downsample_data.downsample_data(curated_dir_path = curated_dir_path,
                                resampled_dir_path = resampled_dir_path,
                                model_input_dir_path = model_input_dir_path,
                                crop_size = model_input_size,
                                new_spacing = model_input_spacing,
                                has_manual_seg = has_manual_seg,
                                num_cores = num_cores)

# model input data preparation
input_data_prep.input_data_prep(resampled_dir_path = resampled_dir_path,
                                model_input_dir_path = model_input_dir_path,
                                create_test_set = create_test_set,
                                crop_size = model_input_size,
                                new_spacing = model_input_spacing,
                                has_manual_seg = has_manual_seg,
                                fill_mask_holes = fill_mask_holes)

# model inference
run_inference.run_inference(model_output_dir_path = model_output_dir_path,
                            model_input_dir_path = model_input_dir_path,
                            model_weights_dir_path = model_weights_dir_path,
                            crop_size = model_input_size,
                            export_png = export_png,
                            model_down_steps = down_steps,
                            extended = extended,
                            has_manual_seg = has_manual_seg,
                            weights_file_name = weights_file_name,
                            mgpu = number_of_gpus)


# post-processing (upsample)
upsample_results.upsample_results(curated_dir_path = curated_dir_path,
                                  resampled_dir_path = resampled_dir_path,
                                  model_output_dir_path = model_output_dir_path,
                                  model_output_nrrd_dir_path = model_output_nrrd_dir_path,
                                  num_cores = num_cores)
