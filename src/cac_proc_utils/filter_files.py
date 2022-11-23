import argparse
import csv
import  os
import shutil


def run_parser():
    parser = argparse.ArgumentParser(description="filter_files.py\n Can create a list of files in a dir of specific type "
                                                 "or take a list of file names (no extension) and remove then from a specific dir\n"
                                                 "running 'filter_files.py -g' will generate a filter list in current directory")
    parser.add_argument('-f','--file', type=str, nargs=1,default='skip_file_list.csv', help="filter list filename (output if in generate mode -g) input if filtering")
    parser.add_argument('-d','--dir', type=str, nargs=1, help='Directory to get file list from (generate mode) or filter')
    parser.add_argument('-e','--ext', type=str, nargs=1, default='.png',help='File extension to find files of.')
    parser.add_argument('-g','--generate',action='store_true')
    return parser.parse_args()

def create_file_list( dir, file_type, output_name=None):
    if output_name is None:
        output_name = "skip_file_list.csv"
        output_name = os.path.join(dir, output_name)

    print('Creating filter list of {} files in directory {} output to {}'.format(file_type, dir, output_name))
    with open(output_name, 'wb') as f:
        writer = csv.writer(f)
        for file in os.listdir(dir):
            if file.endswith(file_type):
                print('Adding: {}'.format(file[:file.rfind(file_type)]))
                writer.writerow([str(file[:file.rfind(file_type)])])



def filter_dir( filter_dir, list_filename, outdir_name=None):
    if outdir_name is None:
        outdir_name = os.path.join(filter_dir, 'filtered')

    if not os.path.exists(outdir_name):
        os.mkdir(outdir_name)

    filter_list = []
    with open(list_filename,'r') as f:
        reader = csv.reader(f)
        for row in reader:
            filter_list.append(row[0])

    for filter in filter_list:
        print('Filter {}'.format(filter))
        files_in_dir = os.listdir(filter_dir)
        for file in files_in_dir:
            if  filter in file:
                fullfilename = os.path.join(filter_dir, file)
                outfilename = os.path.join(outdir_name, file)
                print('Moving {} to {}'.format(fullfilename, outfilename))
                shutil.move(fullfilename, outfilename)





if __name__ == "__main__":

    args = run_parser()
    if args.dir is None:
        args.dir = os.getcwd()
    if( args.generate):
        create_file_list(args.dir, args.ext, args.file)
    else:
        filter_dir(args.dir, args.file)


