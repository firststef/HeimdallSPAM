import argparse
import os
import subprocess

from heimdall_train import heimdall_train
from main import scan, scan2

def parse_status_file(status_file):
    with open(status_file) as f:
        lines = f.readlines()
    expected_status = {}
    paths = {}
    for line in lines:
        path, status = line.strip().split()
        for filename in os.listdir(path):
            expected_status[filename] = status
        paths[path] = status
    return expected_status, paths

def run_spam_filter(file_dirs):
    content = ''
    for dir in file_dirs:
        scan2(dir, "output.txt")
        with open('output.txt', 'r') as f:
            c = f.read()
            content += c
    return content

def parse_spam_filter_output(output):
    actual_status = {}
    for line in output.split('\n'):
        if line.strip() == '':
            continue
        try:
            path, status = line.strip().split("|")
            actual_status[path] = status
        except ValueError:
            continue
    return actual_status

def compare_status(expected, actual):
    matching = 0
    false_positives = 0
    false_negatives = 0
    log = ''
    for path, expected_status in expected.items():
        if path in actual:
            actual_status = actual[path]
            log += f"{path}|expected={expected_status}|actual={actual_status}=>"
            if expected_status == actual_status:
                matching += 1
                log += 'match'
            elif expected_status == "cln" and actual_status == "inf":
                false_positives += 1
                log += 'fp'
            elif expected_status == "inf" and actual_status == "cln":
                false_negatives += 1
                log += 'false_negative'
            log += '\n'

    with open('log.txt', 'w') as f:
        f.write(log)

    total = len(expected)
    matching_percentage = 100 * matching / total
    false_positives_percentage = 100 * false_positives / total
    false_negatives_percentage = 100 * false_negatives / total
    return (matching_percentage, false_positives_percentage, false_negatives_percentage)

def test_spam_filter(status_file):
    expected_status, file_dirs = parse_status_file(status_file)

    # train classifier
    # heimdall_train(file_dirs)

    output = run_spam_filter(file_dirs.keys())
    actual_status = parse_spam_filter_output(output)
    matching_percentage, false_positives_percentage, false_negatives_percentage = compare_status(expected_status, actual_status)
    print(f"""perf: {matching_percentage}% of the files match
    {false_positives_percentage}% were FP marked as `inf` but were actually `cln`
    {false_negatives_percentage}% were FN marked as `cln` but were actually `inf`
    """)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("status_file", help="Path to the file containing the expected status of the files")
    args = parser.parse_args()

    status_file = args.status_file

    test_spam_filter(status_file)
