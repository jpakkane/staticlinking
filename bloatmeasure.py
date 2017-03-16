#!/usr/bin/env python3

#  Copyright (C) 2017 Jussi Pakkanen.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of version 3, or (at your option) any later version,
# of the GNU General Public License as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os
from glob import glob
import subprocess

bins = glob('/usr/bin/*')

skip_lib_strs = ('linux-vdso',
                 'libdl.',
                 'ld-linux-',
                 'libpthread',
                 'libc.',
                 'libm.',
                 'libstdc++',
                 'libgcc_s')

lib_sizes = {}
lib_counts = {}

for b in bins:
    pc  = subprocess.Popen(['ldd', b], universal_newlines=True, stdout=subprocess.PIPE)
    (stdo, _) = pc.communicate()
    if pc.returncode != 0:
        continue
    for line in stdo.split('\n'):
        if '=>' not in line:
            continue
        if 'not found' in line:
            continue
        soname, fname = line.split('=>')
        soname = soname.strip()
        fname = fname.strip().split()[0]
        skip_this = False
        for skip in skip_lib_strs:
            if skip in soname:
                skip_this = True
                break
        if skip_this:
            continue
        if fname in lib_counts:
            lib_counts[fname] += 1
        else:
            lib_sizes[fname] = os.stat(fname).st_size
            lib_counts[fname] = 1

expanded_data = 0
original_data = 0

statfile = open('stats.txt', 'w')
for i in lib_sizes.keys():
    expanded_data += lib_counts[i]*lib_sizes[i]
    original_data += lib_sizes[i]
    statfile.write('%s %d %d\n' % (i, lib_counts[i], lib_sizes[i]))

print('Original size %d, expanded size %d, ratio %f.' % (original_data, expanded_data, original_data/expanded_data))
