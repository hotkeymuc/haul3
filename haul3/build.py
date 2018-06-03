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