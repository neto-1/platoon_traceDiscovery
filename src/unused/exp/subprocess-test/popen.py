#!/usr/bin/env python
"""
Test subprocess return values
"""
from __future__ import print_function
import subprocess
import platform
import json

def get_process_return_value(process, verbose=False):
    """
    Get the return value of process (i.e. the last print statement)
    :param process: The process returned from subprocess.popen
    :param verbose: Whether or not the output of the process should be printed
    """
    output = None

    # poll will return the exit code if the process is completed otherwise it returns null
    while process.poll() is None:
        line = process.stdout.readline()
        if not line:
            break
        output = line # last print statement
        if verbose:
            print(line.rstrip().decode('utf-8'))

    return json.loads(output) # parse JSON

def main():
    """
    Run main method
    """
    # Call Python subprocess
    #print("== Call Python Subprocess ==")
    #cmd = 'python ./foo.py {}'.format(platform.system())
    #process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    #obj = get_process_return_value(process, True)
    #print("\nOutput:", obj)
    #print("\nOutput System:", obj['system'])

    # Call R subprocess
    print("\n== Call R Subprocess ==")
    cmd = 'Rscript ./foo.r {}'.format(platform.system())
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)

    obj = get_process_return_value(process, True)
    print("\nOutput:", obj)
    print("\nOutput System:", obj['system'])

if __name__ == '__main__':
    main()
