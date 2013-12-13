from __future__ import print_function
import re
import os
import sys
import ctypes
from numbapro.findlib import find_lib, find_file

if sys.platform == 'win32':
    _dllopener = ctypes.WinDLL
elif sys.platform == 'darwin':
    _dllopener = ctypes.CDLL
else:
    _dllopener = ctypes.CDLL

def get_libdevice(arch):
    libdir = (os.environ.get('NUMBAPRO_LIBDEVICE') or
              os.environ.get('NUMBAPRO_CUDALIB'))
    pat = r'libdevice\.%s(\.\d+)*\.bc$' % arch
    candidates = find_file(re.compile(pat), libdir)
    return max(candidates) if candidates else None


def open_libdevice(arch):
    with open(get_libdevice(arch), 'rb') as bcfile:
        return bcfile.read()


def get_cudalib(lib, platform=None):
    libdir = os.environ.get('NUMBAPRO_CUDALIB')
    candidates = find_lib(lib, libdir, platform)
    return max(candidates) if candidates else None


def open_cudalib(lib, ccc=False):
    path = get_cudalib(lib)
    if path is None:
        raise OSError('library %s not found' % lib)
    if ccc:
        return ctypes.CDLL(path)
    return _dllopener(path)


def test(_platform=None):
    failed = False
    libs = 'cublas cusparse cufft curand nvvm'.split()
    for lib in libs:
        path = get_cudalib(lib, _platform)
        print('Finding', lib)
        if path:
            print('\tlocated at', path)
        else:
            print('\tERROR: can\'t locate lib')
            failed = True

        if not failed and _platform in (None, sys.platform):
            try:
                print('\ttrying to open library', end='...')
                open_cudalib(lib, ccc=True)
                print('\tok')
            except OSError, e:
                print('\tERROR: failed to open %s:\n%s' % (lib, e))
                failed = True

    archs = 'compute_20', 'compute_30', 'compute_35'
    for arch in archs:
        print('\tfinding libdevice for', arch, end='...')
        path = get_libdevice(arch)
        if path:
            print('\tok')
        else:
            print('\tERROR: can\'t open libdevice for %s' % arch)
            failed = True
    return not failed

