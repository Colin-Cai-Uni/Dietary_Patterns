import pandas as pd
import argparse
import os

'''
A simple script to append the cluster labels from one csv file to another.

Parameters
----------
datafile : file location
    Location of the file to apply the labels to.
labelfile : file location
    Location of the file to extract the labels to.
incol : string
    The name of the column that stores the cluster labels in the 
    label file.
outpuftfolder : file location
    The path to where the newly labeled data file should be saved.
outcol : string
    The name of the column that will encode the cluster labels in the 
    newly labeled data file.
'''
def main():
    directory = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', help = 'Data file')
    parser.add_argument('labelfile', help = 'Label file')
    parser.add_argument('incol', help = 'Input label column')
    parser.add_argument('outputfile', help = 'Output file')
    parser.add_argument('outcol', help = 'Output label file')

    args = parser.parse_args()

    data = pd.read_csv(os.path.join(directory, args.datafile))
    data[args.incol] = pd.read_csv(os.path.join(directory, args.labelfile))[args.outcol]
    data.to_csv(os.path.join(directory, args.outputfile), index = False)

if __name__ == "__main__":
    main()