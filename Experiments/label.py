import pandas as pd
import argparse
import os

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