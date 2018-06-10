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



### Set up external tool paths
os.environ['QEMU_PATH']  = 'Z:/Apps/_emu/qemu';

#os.environ['JRE_PATH']  = 'C:/Program Files/Java/jre1.8.0_151'
#os.environ['JRE_PATH']  = 'C:/Program Files/Java/jdk1.7.0_75'
os.environ['JRE_PATH']  = 'Z:/Apps/_code/AndroidStudio/jre'

#os.environ['ANDROID_SDK_HOME']  = 'Z:/Data/_code/_sdk/adt-bundle-windows-x86-20130522/sdk';

#os.environ['ARDUINO_PATH'] = 'C:/Apps/_code/Arduino';
os.environ['ARDUINO_PATH'] = 'Z:/Apps/_code/Arduino';
os.environ['EMULARE_PATH'] = 'Z:/Apps/_emu/ArduinoEmu/emulare_1.9';

#os.environ['Z88DK_PATH'] = 'C:/Apps/_code/z88dk.git';
os.environ['Z88DK_PATH'] = 'Z:/Data/_code/_cWorkspace/z88dk.git';
os.environ['MESS_PATH'] = 'Z:/Apps/_emu/MESSUI-0.190';
os.environ['MESS_ROM_PATH'] = 'Z:/Apps/_emu/_roms';

os.environ['GBDK_PATH'] = os.path.abspath('tools/platforms/gameboy/gbdk');
os.environ['BGB_PATH'] = os.path.abspath('tools/platforms/gameboy/bgb');

os.environ['POSE_PATH'] = os.path.abspath('tools/platforms/palmos/pose');

#os.environ['PalmSDK'] = '';


### Create project
example_name = 'hello'
#example_name = 'small'
#example_name = 'shellmini'
#example_name = 'hio_test'
#example_name = 'hres_test'

p = HAULProject(example_name)
p.sources_path = 'examples'
p.libs_path = 'libs'
p.ress_path = 'examples'


# Add libs that are available for importing
#p.add_lib('hio')
#p.add_lib('hres')

p.add_source(example_name)

p.add_res('hres_data1.txt')
p.add_res('hres_data2.txt')

p.run_test = True



### Do the building
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


builder.build(p)
#builder.translate()
#builder.compile()
#builder.package()
#builder.test()
#builder.finish()


put('build.py ended.')