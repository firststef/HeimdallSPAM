import argparse
import os
import sys

from heimdall_spam import hd_filter, hd_filter_multi

def info(output_file):
    project_name = "Heimdall SPAM"
    student_name = "Petrovici Stefan"
    alias = "SPE"
    version = "3.0"
    with open(output_file, "w") as f:
        f.write(f"""{project_name}
{student_name}
{alias}
{version}""")

def scan(folder, output_file):
    with open(output_file, "w") as f:
        for filename in os.listdir(folder):
            verdict = "cln"

            # call spam library
            verdict = hd_filter(f"{folder}/{filename}")

            f.write(f"{filename}|{verdict}\n")

def scan2(folder, output_file):
    with open(output_file, "w") as f:
        # call spam library
        for filename, verdict in hd_filter_multi(folder):
            f.write(f"{filename}|{verdict}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-info", help="write information about the project to the specified file", metavar="output_file")
    parser.add_argument("-scan", help="scan the specified folder and write the results to the specified file", nargs=2, metavar=("folder", "output_file"))
    args = parser.parse_args()
    if args.info:
        info(args.info)
    elif args.scan:
        scan2(args.scan[0], args.scan[1])
    else:
        print("Invalid arguments. Use -h to see the usage.")
        sys.exit(1)
