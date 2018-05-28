# HAUL3
HotKey's Amphibious Universal Language

The goal of HAUL is to have a piece of code that can translate itself into any other language. On its journey it can -of course- translate other source code as well.

![Hello HAUL](https://github.com/hotkeymuc/haul/raw/master/haul3/data/media/build_hello.gif "Hello HAUL")

This is in no way intended for any productive use. It's food for thought. An elaborate toy. Art and fart.

Have fun with it and don't hurt your brain.

//HotKey


## Version 3 (2013-01 - now)
* This version can not yet translate its own source, but it's getting very close.
* In the meantime it can translate whatever other source code you throw at it.
* Finally, I am using a proper AST structure (modules, functions, expressions, instructions, ...)
* Just doing it the way everyone else does it: Lex it, parse it, generate output. Boring, yet powerful. Now, translation to binary output is finally feasible.
* This is the most OOP approach yet. Much easier to comprehend than the previous versions, which streamed the tokens on-the-fly.
* The source language "HAL3" is now just valid python, eliminating the "chicken-egg-problem" of the previous versions.
* No boot strapping is needed any more, since all parts of the source are runnable.
* Pro: Pretty easy to add a new output language.
* Con: High memory consumption (keeps the whole AST structure in RAM), so it may get hard to create a C64 output module.

## Usage
* Write your code in HAL3 (which is valid python). You need to annotate some variable types where inference is not possible. Use either Python3 colons or *#@var NAME TYPE* comments for that.
* Use *translate.py* to translate that file into the desired target language.
* Use *ide.py* to play around with different languages.
* Use *build.py* to also compile/bundle/package/test the file on different architectures. This, unfortunately, requires external tools (QEMU, gcc, SDKs), which I regard as cheating.

![HAUL IDE](https://github.com/hotkeymuc/haul/raw/master/haul3/data/media/ide_screenshot000.png "HAUL IDE")

## Directory Structure
* *haul* holds the main source code, including the parser(s) and builders
* *data* holds language/platform specific data, e.g. native libraries or resources
* *examples* holds some example code, ready to be translated to any other language
* *tools* holds external tools that are needed for some builders, e.g. emulators, compilers and SDKs
