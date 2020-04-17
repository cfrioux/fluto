"""
Definition of constants, for paths, names, arguments for ASP solvers.
Moreover, some generalist functions are defined,
 notabily for solving management and logging.
"""

import sys
import os

# Root
ROOT = __file__.rsplit('/', 1)[0]


# Constants
ASP_FILE_EXTENSION = '.lp'

# Directories (starting from here)
DIR_SOURCES     = ''  # sources are inside the package
DIR_ASP_SOURCES = '/encodings/'
DIR_DATA     = ROOT + '/../data/'  # sources are inside the package

# ASP SOURCES
def __asp_file(name):
    "path to given asp source file name"
    return ROOT + DIR_ASP_SOURCES + name + ASP_FILE_EXTENSION
# Routine
ASP_SRC_UNPROD = __asp_file('unproducible_targets')
# Hybrid gap-flling Fluto
ASP_SRC_FLUTO   = __asp_file('top-gf-encoding')

def basename(filepath):
    """Return the basename of given filepath.
    >>> basename('~/ASP/test/adirectory/plop.lp')
    'fly'
    """
    return os.path.splitext(os.path.basename(filepath))[0]

def extension(filepath):
    """Return the extension of given filepath.
    >>> extension('~/ASP/test/adirectory/plop.lp')
    'lp'
    >>> extension('whatisthat')
    ''
    >>> extension('whatis.that')
    'that'
    """
    return os.path.splitext(os.path.basename(filepath))[1][1:]

def is_valid_path(filepath):
    """True iff given filepath is a valid one (a file exists, or could exists)"""
    if filepath and not os.access(filepath, os.W_OK):
        try:
            open(filepath, 'w').close()
            os.unlink(filepath)
            return True
        except OSError:
            return False
    else:  # path is accessible
        return True
