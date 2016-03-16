# Licensed under a 3-clause BSD style license - see PYFITS.rst
from __future__ import (print_function, absolute_import, division,
                        unicode_literals)

import os
import platform
from pprint import pprint
import subprocess as sp
import struct

from distutils.core import Extension

from astropy_helpers import setup_helpers
from astropy_helpers.distutils_helpers import get_distutils_build_option


def get_extensions():
    ulist = platform.uname()
    xpa_dir = os.path.join('cextern', 'xpa')
    debug = get_distutils_build_option('debug')

    # libxpa configurations
    cfg = setup_helpers.DistutilsExtensionArgs()
    cfg['extra_compile_args'].append('-DHAVE_CONFIG_H')

    if 'CFLAGS' not in os.environ and struct.calcsize("P") == 4:
        if ulist[0] == 'Darwin' or ulist[4] == 'x86_64':
            if debug:
                print('adding -m32 to compiler flags ...')
            cflags = '-m32'
            cfg['extra_compile_args'].append(cflags)

    # cfg['extra_compile_args'].extend([# '--enable-shared',
    #                                   '--without-tcl',
    #                                   cflags])

    # import pdb; pdb.set_trace()

    if not setup_helpers.use_system_library('libxpa'):
        if not debug:
            # All of these switches are to silence warnings from compiling
            cfg['extra_compile_args'].extend([
                '-Wno-declaration-after-statement',
                '-Wno-unused-variable', '-Wno-parentheses',
                '-Wno-uninitialized', '-Wno-format',
                '-Wno-strict-prototypes', '-Wno-unused', '-Wno-comments',
                '-Wno-switch', '-Wno-strict-aliasing', '-Wno-return-type',
                '-Wno-address', '-Wno-unused-result'
            ])

        cfg['include_dirs'].append(xpa_dir)
        sources = ['xpa.c', 'xpaio.c', 'command.c', 'acl.c', 'remote.c',
                   'clipboard.c', 'port.c', 'tcp.c', 'client.c', 'word.c',
                   'xalloc.c', 'find.c', 'xlaunch.c', 'timedconn.c',
                   'tclloop.c', 'tcl.c']
        cfg['sources'].extend([os.path.join(xpa_dir, s) for s in sources])
    else:
        cfg.update(setup_helpers.pkg_config(['libxpa'], ['libxpa']))

    libxpa = Extension('pyds9.libxpa', **cfg)

    return [libxpa, ]


def get_package_data():
    # Installs the testing data files
    return {
        'pyds9.tests': [os.path.join('data', '*.fits')]}


def get_external_libraries():
    return ['libxpa']


def post_build_ext_hook(cmd):
    "Build the xpans executable"
    compiler = cmd.compiler
    libxpa = cmd.ext_map['pyds9.libxpa']
    flags = libxpa.extra_compile_args
    include_dirs = libxpa.include_dirs
    file_name = libxpa._file_name
    build_lib = cmd.build_lib
    build_temp = cmd.build_temp

    # use distutils compiler to build the xpans.o
    xpans_c = os.path.join('cextern', 'xpa', 'xpans.c')
    compiler.compile([xpans_c, ], output_dir=build_temp,
                     include_dirs=include_dirs,
                     debug=get_distutils_build_option('debug'),
                     extra_postargs=flags, depends=[xpans_c, ])
    import pdb; pdb.set_trace()
    # compile the executable by hand
    xpans_o = os.path.join(build_temp, xpans_c.replace('.c', '.o'))
    xpans = os.path.join(build_lib, cmd.distribution.get_name(), 'xpans')
    libxpa_so = os.path.join(build_lib, file_name)
    compile_cmd = compiler.compiler
    compile_cmd += [xpans_o, '-o', xpans, libxpa_so]
    compile_cmd += flags
    print(" ".join(compile_cmd))
    sp.check_call(compile_cmd)




def post_install_hook(cmd):
    pprint(cmd.__dict__)
    import pdb; pdb.set_trace()


def requires_2to3():
    return False
