import os
import shutil
import argparse
import numpy as np

from pathlib import Path

chars = list('!abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
dir_names = ['src', 'bin', 'docs', 'test', 'logs']
file_names = ['README.md', 'config.yaml', 'requirements.txt', 'index.html', 'document.pdf']
exe_names = ['main.o', 'setup.exe', 'run.sh', 'app.js', 'entrypoint.sh']

class Zip_Generator:
    def __init__(self, args):
        super(Zip_Generator, self).__init__()
        self.args = args
        self.root = './tmp'
        self.tar_name = 'target.pdf'

        base_path = Path(__file__).parent.resolve()
        self.bait = str(base_path / 'sample' / 'document.pdf')
        self.script = str(base_path / 'sample' / 'script.bat')
        
    def build_normal(self, root:str, depth:int):
        if depth > self.args.max_depth:
            return False
        os.mkdir(root)
        num_dir, num_file = np.random.randint(low=1, high=4, size=2)
        # build files
        for idx in range(num_file):
            is_exe = np.random.randint(low=0, high=2, size=1)
            if is_exe:
                n_idx = np.random.randint(low=0, high=len(exe_names), size=1)[0]
                shutil.copyfile(self.script, os.path.join(root, exe_names[n_idx]))
            else:
                n_idx = np.random.randint(low=0, high=len(file_names), size=1)[0]
                shutil.copyfile(self.bait, os.path.join(root, file_names[n_idx]))
        # build directories
        d_indices = np.random.choice(np.arange(0, len(dir_names)), size=num_dir, replace=False)
        for idx in d_indices:
            _ = self.build_normal(root=f'{root}/{dir_names[idx]}', depth=depth+1)
        return True

    def locate_target(self):
        if 'fec' in self.args.rules:
            assert self.args.tar_layer < self.args.max_depth
        # list directories satisfied the target layer
        tar_list = []
        file_list = list(Path(self.root).rglob('*'))
        for file in file_list:
            if file.is_dir() and (len(str(file).split('/'))-1 == self.args.tar_layer):
                tar_list.append(str(file))
        # random select one directories
        np.random.shuffle(tar_list)
        return tar_list[0]

    def build_rules(self):
        self.seed_dict = {}
        # w1: build target file
        if 'tw' in self.args.rules:
            self.tar_name += ' '
            shutil.copyfile(self.bait, os.path.join(self.tar_path, self.tar_name))
        else:
            shutil.copyfile(self.bait, os.path.join(self.tar_path, self.tar_name))
        # w2: build file/dir at the same layer
        if 'fdc' in self.args.rules:
            self.seed_dict['fdc'] = ''.join(np.random.choice(chars, size=len(self.tar_name)))
            os.mkdir(f'{self.tar_path}/{self.seed_dict["fdc"]}')
        # w3: build file/dir at the diff layer
        if 'fec' in self.args.rules:
            # check all directories at the same layer
            dir_list = []
            file_list = list(Path(self.tar_path).rglob('*'))
            for file in file_list:
                if file.is_dir():
                    dir_list.append(file)
            if len(dir_list) == 0:
                d_idx = np.random.randint(low=0, high=len(dir_names), size=1)[0]
                d_name = dir_names[d_idx]
                os.mkdir(f'{self.tar_path}/{d_name}')
            else:
                np.random.shuffle(dir_list)
                d_name = dir_list[0].name
            # build executable
            d_path = f'{self.tar_path}/{d_name}'
            num_nest = np.random.randint(low=0, high=3, size=1)[0]
            for idx in range(num_nest):
                d_path += f'/{d_name}'
                os.mkdir(d_path)
            shutil.copyfile(self.script, os.path.join(d_path, f'{self.tar_name}.bat'))
        return True
            
    def build_zip(self):
        shutil.make_archive(self.root, 'zip', self.root)
        with open(f'{self.root}.zip', 'rb') as f:
            content = f.read()
            if 'fdc' in self.args.rules:
                content = content.replace(f'{self.seed_dict["fdc"]}'.encode(), self.tar_name.encode())
        os.remove(f'{self.root}.zip')

        with open(self.args.g_output, 'wb') as f:
            f.write(content)

        return True

    def build(self):
        _ = self.build_normal(root=self.root, depth=1)
        self.tar_path = self.locate_target()
        _ = self.build_rules()
        _ = self.build_zip()
        shutil.rmtree(self.root)
        if 'tw' in self.args.rules:
            self.tar_name = self.tar_name[:-1]