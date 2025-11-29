import os
import argparse
import zipfile

from src.rules import Zip_Rules
    
def get_args_parser():
    parser = argparse.ArgumentParser('Zip test')
    parser.add_argument('--test_env',   type=str, default='./tests/benign/')
    parser.add_argument('--zip_file',   type=str, default='CVE-2023-38831-2.rar')   
    return parser

if __name__ == "__main__":
    args = get_args_parser()
    args = args.parse_args()

    zip_file = zipfile.ZipFile(args.test_env+args.zip_file, 'r')
    tester = Zip_Rules(show_details=True)
    
    flag_1 = tester.trailing_whitespace(zip_file)
    flag_2 = tester.abnormal_executable(zip_file, 0.2)
    flag_3 = tester.file_dir_collision(zip_file)
    flag_4 = tester.deep_nested_executable(zip_file, 2)

    print('[Info] check result:')
    print(f'--- Trailing Whitespace    : {flag_1}')
    print(f'--- Abnormal Executable    : {flag_2}')
    print(f'--- File Dir Collision     : {flag_3}')
    print(f'--- Deep Nested Executable : {flag_4}')