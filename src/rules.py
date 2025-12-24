import zipfile

import src.utils as utils

class Zip_Rules:
    def __init__(self, show_details:bool=False):
        super(Zip_Rules, self).__init__()
        self.show_details = show_details

    def trailing_whitespace(self, file:zipfile.ZipFile):
        check = False
        for zinfo in file.infolist():
            if zinfo.is_dir():
                _name = zinfo.filename[:-1]
            else:
                _name = zinfo.filename

            if _name != _name.rstrip(' '):
                check = True
                if self.show_details:
                    print(f'[Warn] "{zinfo.filename}" has trailing whitespace')
        return check

    # def file_exe_collision(self, file:zipfile.ZipFile):
    #     _record = {}
    #     check = False
    #     for zinfo in file.infolist():
    #         if zinfo.is_dir():
    #             _name = zinfo.filename[:-1].split('/')[-1]
    #             _record[_name] = True
    #         else:
    #             _name = zinfo.filename.split('/')[-1]
    #             _idx = _name.rfind('.')
    #             _prev, _ext = _name[:_idx], _name[_idx+1:]
    #             # w1: check executable
    #             if _ext not in ['bat', 'cmd', 'exe']:
    #                 _record[_name] = True
    #                 _record[_prev] = True
    #             # w2: abnormal check
    #             else:
    #                 if _prev in _record.keys():
    #                     check = True
    #                     if self.show_details:
    #                         print(f'[Warn] "{zinfo.filename}" collide with file')
    #     return check

    def dir_exe_collision(self, file:zipfile.ZipFile):
        _record = {}
        check = False
        for zinfo in file.infolist():
            if not zinfo.is_dir():
                _names = zinfo.filename.split('/')
                _d_names, _f_name = _names[:-1], _names[-1]
                _idx = _f_name.rfind('.')
                _prev, _ext = _f_name[:_idx], _f_name[_idx+1:]
                # w1: check executable
                if _ext in ['bat', 'cmd', 'exe']:
                    # w1-2: abnormal check
                    if _prev in _d_names:
                        check = True
                        if self.show_details:
                            print(f'[Warn] "{zinfo.filename}" collide with directory')
        return check

    def file_dir_collision(self, file:zipfile.ZipFile):
        # Build Group
        _layer = {}
        for zinfo in file.infolist():
            _parent = [path for path in zinfo.filename.split('/') if path]
            _parent = tuple(_parent[:-1])
            if _parent not in _layer.keys():
                _layer[_parent] = []
            _layer[_parent].append((zinfo.is_dir(), zinfo.filename))
        # check collision
        check = False
        for key, attrs in _layer.items():
            _file, _dir = [], []
            for (is_dir, filename) in attrs:
                if is_dir:
                    _name = filename[:-1]
                    _dir.append(_name)
                    if _name in _file:
                        check = True
                        if self.show_details:
                            print(f'[Warn] "{filename}" collide with file')
                else:
                    _name = filename
                    _file.append(_name)
                    if _name in _dir:
                        check = True
                        if self.show_details:
                            print(f'[Warn] "{filename}" collide with directory')
        return check

    def deep_nested_executable(self, file:zipfile.ZipFile, threshold:int):
        # Build Group
        _layer = {}
        for zinfo in file.infolist():
            _parent = [path for path in zinfo.filename.split('/') if path]
            _parent = tuple(_parent[:-1])
            if _parent not in _layer.keys():
                _layer[_parent] = []
            _layer[_parent].append((zinfo.is_dir(), zinfo.filename))
        # check executable
        check = False
        for key, attrs in _layer.items():
            # w1: deep-nested layers
            if len(key) < threshold:
                continue
            # w2: executable
            for (is_dir, filename) in attrs:
                if not is_dir and filename.split('.')[-1] in ['bat', 'cmd', 'exe']:
                    check = True
                    if self.show_details:
                        print(f'[Warn] "{filename}" is deep-nested')
        return check