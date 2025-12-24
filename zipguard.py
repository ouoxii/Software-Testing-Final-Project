import os
import re
import argparse
import zipfile
import numpy as np

from pathlib import Path
from src.rules import Zip_Rules
from src.generator import Zip_Generator

def verify(args):
    if args.zip_path is None:
        print('[Info] no test environment.')
    if args.zip_file is None:
        names = [str(name) for name in Path(args.zip_path).glob("*")]
        names = sorted(names, key = lambda name: tuple(map(int, re.findall(r'\d+', name))))
    else:
        names = [args.zip_path+args.zip_file]

    with open(args.v_output, 'w') as f:
        pass

    result = {}
    tester = Zip_Rules(show_details=False)
    for name in names:
        file = zipfile.ZipFile(name, 'r')

        flag_1 = tester.trailing_whitespace(file)
        flag_2 = tester.dir_exe_collision(file)
        flag_3 = tester.file_dir_collision(file)
        flag_4 = tester.deep_nested_executable(file, 3)

        result[name] = flag_1 and flag_2 and flag_3

        infos = [
            f'[Info] {name} check result:',
            f'--- Trailing Whitespace    : {flag_1}',
            f'--- Dir Exe Collision      : {flag_2} ( Prev: Abnormal Executable )',
            f'--- File Dir Collision     : {flag_3}',
            f'--- Deep Nested Executable : {flag_4}'
        ]
        with open(args.v_output, 'a') as f:
            np.savetxt(f, infos, fmt='%s')

    check = False
    for key, val in result.items():
        if val:
            check = True
            print(f'[Info] {key} is suspicious')
    if not check:
        print('[Info] No suspicious zip file detected')

def generate(args):
    np.random.seed(args.seed)
    gen = Zip_Generator(args=args)
    for idx in range(args.g_num):
        args.g_output = args.g_path + f'output_{idx}.rar'
        gen.build()

def get_args_parser():
    parser = argparse.ArgumentParser('Zip test')
    parser.add_argument('--mode',       type=str, default='v')
    # verify zip file
    parser.add_argument('--zip_path',   type=str, default=None)
    parser.add_argument('--zip_file',   type=str, default=None)   
    parser.add_argument('--v_output',   type=str, default='./result.txt')
    # generate zip file
    parser.add_argument('--seed',       type=int, default=42)
    parser.add_argument('--max_depth',  type=int, default=3)
    parser.add_argument('--tar_layer',  type=int, default=1)
    parser.add_argument('--rules',      type=str, default='tw-fec-fdc')
    parser.add_argument('--g_num',      type=int, default=1)
    parser.add_argument('--g_path',   type=str, default='./tests/generate/')
    return parser

if __name__ == "__main__":
    args = get_args_parser()
    args = args.parse_args()
    args.rules = args.rules.split('-')

    if args.mode == 'v':
        verify(args)
    elif args.mode == 'g':
        generate(args)
    else:
        print(f'[Warn] activate zipguard with wrong mode: {args.mode}')

    