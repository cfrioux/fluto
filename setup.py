#!/usr/bin/env python
# Copyright (c) 2018, Clemence Frioux <clemence.frioux@gmail.com>
#
# This file is part of fluto.
#
# MeneTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MeneTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fluto.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name             = 'fluto',
    version          = '1.0.0',
    url              = 'https://github.com/cfrioux/fluto',
    license          = 'GPLv3+',
    description      = 'Hybrid gap-filling tool',
    long_description = 'Hybrid gap-filling tool for metabolic models. Fluto proposes solutions that fit constraint-based and graph-based modelings. \
More information on usage and troubleshooting on Github: https://github.com/cfrioux/fluto',
    author           = 'Clemence Frioux',
    author_email     = 'clemence.frioux@gmail.com',
    packages         = ['__fluto__'],
    package_dir      = {'__fluto__' : 'src'},
    package_data     = {'__fluto__' : ['encodings/*.lp']},
    scripts          = ['fluto.py'],
)
