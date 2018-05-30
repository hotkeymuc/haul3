# HAUL3 (2013-01 - now)
HotKey's Amphibious Universal Language

The goal of HAUL is to have a piece of code that can translate itself into any other language. On its journey it can -of course- translate other source code as well.

![Hello HAUL](https://github.com/hotkeymuc/haul/raw/master/haul3/data/media/build_hello.gif "Hello HAUL")

This kind of program is nothing new, nothing special. Every programmer should have tried this at least once themself. (See: [Transpiler](https://en.wikipedia.org/wiki/Source-to-source_compiler), [Quine](https://en.wikipedia.org/wiki/Quine_(computing)), [LLVM](https://llvm.org/), etc.) Well, this is just my own approach at that.

This project is in no way intended for any productive use. It's food for thought. An elaborate toy. Art and fart.

Have fun with it and don't hurt your brain.

//HotKey


## Versions
This project is based on [HAUL2](https://github.com/hotkeymuc/haul2) which did not use a dedicated lexer/parser/AST. It was therefore much simpler and limited.

If you are curious for the origins of this project, then have a look at the ugly PHP based first version [HAUL1](https://github.com/hotkeymuc/haul1).

## Features and Limitations
* This version can not *yet* translate its own source, but it's getting very close. At the moment there are quite some "pythonic" statements used in the parser; so they either have to be eliminated *or* implemented in HAL3 as well... In the meantime, feel free to throw other source code at it.
* Finally, HAUL3 is using a proper AST structure, which allows output languages that vastly differ from scripting languages, e.g. JSON or Assembly.
* The source language "HAL3" is now just valid python, eliminating the "chicken-egg-problem" of the previous versions. No more bootstrapping needed.
* This is the most object-oriented approach yet. Much easier to comprehend than the previous versions, but also much more complex and powerful. Finally: Real classes, namespaces, imports, libraries, ...
* + Pro: Pretty easy to add new output languages and features.
* - Con: High memory consumption (keeps a lot of structures in RAM), so it may be hard to run a big compilation on a C64...
* HAUL3 adds the concept of "builders". A builder can translate code into another language and package it for a certain hardware platform. This means, for example, one-click deployment to a PalmOS device :-)

## Usage
* Write your code in HAL3 (which is valid python). You need to annotate some variable types where inference is not possible. Use either Python3 colons or *#@var NAME TYPE* comments for that.
* Use `translate.py` to translate that file into the desired target language.
* Use `ide.py` to play around with different languages.
* Use `build.py` to also compile/bundle/package/test the file on different architectures. This, unfortunately, requires external tools (QEMU, gcc, SDKs), which I regard as cheating.

![HAUL IDE](https://github.com/hotkeymuc/haul/raw/master/haul3/data/media/ide_screenshot000.png "HAUL IDE")

## Directory Structure
* **haul** holds the main source code, including the parser(s) and builders
* **data** holds language/platform specific data, e.g. native libraries or resources
* **examples** holds some example code, ready to be translated to any other language
* **tools** holds external tools that are needed for some builders, e.g. emulators, compilers and SDKs
