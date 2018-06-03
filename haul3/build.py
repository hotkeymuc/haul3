#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from haul.platforms.android.builder_android import *
from haul.platforms.arduino.builder_arduino import *
from haul.platforms.dos.builder_dos import *
from haul.platforms.gameboy.builder_gameboy import *
from haul.platforms.html.builder_html import *
from haul.platforms.java.builder_java import *
from haul.platforms.palmos.builder_palmos import *
from haul.platforms.psion.builder_psion import *
from haul.platforms.vtech.builder_vtech import *
from haul.platforms.webos.builder_webos import *



#source_filename = 'hello.py'
#source_filename = 'small.py'
#source_filename = 'shellmini.py'
#source_filename = 'hres_test.py'
#source_filename = 'hio_test.py'

p = HAULProject('hello')
p.sources_path = 'examples'
p.libs_path = 'libs'

p.add_lib('hio')
p.add_source('hello')
#p.add_resource(...)

p.run_test = True



#builder = HAULBuilder_android()
#builder = HAULBuilder_arduino()
#builder = HAULBuilder_dos()
#builder = HAULBuilder_gameboy()
#builder = HAULBuilder_html()
#builder = HAULBuilder_java()
#builder = HAULBuilder_palmos()
#builder = HAULBuilder_psion()
builder = HAULBuilder_vtech()
#builder = HAULBuilder_webos()


builder.build(p)

#builder.translate()
#builder.compile()
#builder.package()
#builder.test()
#builder.finish()


put('build.py ended.')