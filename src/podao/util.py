import os
import shutil
import tempfile

from contextlib import contextmanager
from functools import wraps

import sh


def check_pyenv():
    try:
        return sh.pyenv('--version')
    except sh.CommandNotFound:
        return False


def check_pyvenv():
    for dir, _, _ in walk_dir_up(os.getcwd(), 2):
        pyvenv = os.path.join(dir, 'pyvenv.cfg')
        if os.path.isfile(pyvenv):
            return dir
        else:
            return False


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def create_dir(root, dir):
    path = os.path.join(root, dir)
    if os.path.exists(path):
        yield f'    {dir} folder already exists, skipping ...'
    else:
        os.mkdir(path)
        yield f'    {dir} created.'


@contextmanager
def atomic_write(path, overwrite=True, encoding='utf-8'):
    if not overwrite and os.path.exists(path):
        yield False
        return

    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    fd, name = tempfile.mkstemp(suffix='-tmp', dir=dir)
    fp = open(fd, 'w', encoding=encoding)

    try:
        yield fp
    except Exception:
        fp.close()
        raise
    else:
        fp.close()
        shutil.copyfile(name, str(path))
    finally:
        os.unlink(name)


def walk_dir_up(cur, max=3):
    cur = os.path.realpath(cur)
    dirs, files = [], []
    for entry in os.scandir(cur):
        if entry.is_dir():
            dirs.append(entry.name)
        elif entry.is_file():
            files.append(entry.name)
    yield cur, dirs, files

    up = os.path.realpath(os.path.join(cur, ".."))
    if up != cur and max > 0:
        yield from walk_dir_up(up, max - 1)
