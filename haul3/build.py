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



source_filename = 'hello.py'
#source_filename = 'small.py'
#source_filename = 'shellmini.py'
#source_filename = 'hres_test.py'
#source_filename = 'hio_test.py'

perform_test_run = True


#builder = HAULBuilder_android()
#builder = HAULBuilder_arduino()
#builder = HAULBuilder_dos()
#builder = HAULBuilder_gameboy()
#builder = HAULBuilder_html()
#builder = HAULBuilder_java()
#builder = HAULBuilder_palmos()
#builder = HAULBuilder_psion()
#builder = HAULBuilder_vtech()
builder = HAULBuilder_webos()


source_path = os.path.abspath('examples')
staging_path = os.path.abspath('staging')
output_path = os.path.abspath('build')
data_path = os.path.abspath('data')
#resources = [
#	os.path.join(source_path, 'hres_data1.txt'),
#	os.path.join(source_path, 'hres_data2.txt'),
#]

builder.set_staging_path(os.path.abspath('staging'))
builder.configure(
	source_path=source_path,
	libs_path='libs',
	staging_path='staging',
	output_path='build',
	data_path='data',
)

builder.prepare()
builder.compile()
builder.package()
builder.test()
builder.finish()



builder.build(
	source_path=source_path,
	source_filename=source_filename,
	output_path=output_path,
	staging_path=staging_path,
	data_path=data_path,
	resources=resources,
	perform_test_run=perform_test_run)

put('build.py ended.')