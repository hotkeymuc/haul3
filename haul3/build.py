#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from haul.platforms.android.haulBuilder_android import *
from haul.platforms.arduino.haulBuilder_arduino import *
from haul.platforms.dos.haulBuilder_dos import *
from haul.platforms.gameboy.haulBuilder_gameboy import *
from haul.platforms.html.haulBuilder_html import *
from haul.platforms.java.haulBuilder_java import *
from haul.platforms.palmos.haulBuilder_palmos import *
from haul.platforms.psion.haulBuilder_psion import *
from haul.platforms.vtech.haulBuilder_vtech import *
from haul.platforms.webos.haulBuilder_webos import *


#builder = HAULBuilder_android()
#builder = HAULBuilder_arduino()
#builder = HAULBuilder_dos()
#builder = HAULBuilder_gameboy()
#builder = HAULBuilder_html()
builder = HAULBuilder_java()
#builder = HAULBuilder_palmos()
#builder = HAULBuilder_psion()
#builder = HAULBuilder_vtech()
#builder = HAULBuilder_webos()

source_filename = 'hello.py'
#source_filename = 'small.py'
#source_filename = 'shellmini.py'
#source_filename = 'hres_test.py'
#source_filename = 'hio_test.py'

source_dir = os.path.abspath('test')
staging_dir = os.path.abspath('staging')
build_dir = os.path.abspath('build')
resources = [
	os.path.join(source_dir, 'hres_data1.txt'),
	os.path.join(source_dir, 'hres_data2.txt'),
]

builder.build(source_filename, source_dir, staging_dir, build_dir, resources=resources, perform_test_run=True)
