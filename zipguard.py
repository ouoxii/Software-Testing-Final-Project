import os
import re
import argparse
import zipfile
import numpy as np

from pathlib import Path
from src.rules import Zip_Rules
    
def get_args_parser():
    parser = argparse.ArgumentParser('Zip test')
    parser.add_argument('--zip_path',   type=str, default=None)
    parser.add_argument('--zip_file',   type=str, default=None)   
    parser.add_argument('--output',     type=str, default='./result.txt')   
    return parser

if __name__ == "__main__":
    args = get_args_parser()
    args = args.parse_args()

    if args.zip_path is None:
        print('[Info] no test environment.')
    if args.zip_file is None:
        names = [str(name) for name in Path(args.zip_path).glob("*")]
        names = sorted(names, key = lambda name: tuple(map(int, re.findall(r'\d+', name))))
    else:
        names = [args.zip_path+args.zip_file]

    with open(args.output, 'w') as f:
        pass

    result = {}
    tester = Zip_Rules(show_details=False)
    for name in names:
        file = zipfile.ZipFile(name, 'r')

        flag_1 = tester.trailing_whitespace(file)
        flag_2 = tester.file_exe_collision(file)
        flag_3 = tester.file_dir_collision(file)
        flag_4 = tester.deep_nested_executable(file, 2)

        result[name] = flag_1 and flag_2 and flag_3

        infos = [
            f'[Info] {name} check result:',
            f'--- Trailing Whitespace    : {flag_1}',
            f'--- Abnormal Executable    : {flag_2}',
            f'--- File Dir Collision     : {flag_3}',
            f'--- Deep Nested Executable : {flag_4}\n'
        ]
        with open(args.output, 'a') as f:
            np.savetxt(f, infos, fmt='%s')

    check = False
    for key, val in result.items():
        if val:
            check = True
            print(f'[Info] {key} is suspicious')
    if not check:
        print('[Info] No suspicious zip file detected')