#!/usr/bin/python
# Copyright (c) 2018, Clemence Frioux <clemence.frioux@gmail.com>
#
# This file is part of fluto.
#
# Fluto is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fluto is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fluto.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name             = 'Flutopy',
    version          = '1.0.0',
    # url              = 'https://github.com/cfrioux/fluto',
    license          = 'GPLv3+',
    description      = 'Hybrid gap-filling tool',
    long_description = 'Hybrid gap-filling tool for metabolic models. Fluto proposes solutions that fit constraint-based (FLUx balance analysis) and graph-based (TOpology) modelings of producibility. \
More information on usage and troubleshooting on Github: https://github.com/cfrioux/fluto',
    author           = 'Clemence Frioux',
    author_email     = 'clemence.frioux@gmail.com',
    packages         = ['flutopy'],
    package_dir      = {'flutopy' : 'flutopy'},
    package_data     = {'flutopy' : ['encodings/*.lp']},
    scripts          = ['fluto.py'],
)
