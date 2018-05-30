# HAUL3
*HotKey's Amphibious Universal Language* Version 3

## About
The goal of HAUL is to have a piece of code that can translate itself into any other language. On its journey it can -of course- translate other source code as well.

![Hello HAUL](https://raw.githubusercontent.com/hotkeymuc/haul3/master/media/build_hello.gif "Hello HAUL")

These kinds of programs are nothing new and nothing *too* special. Every programmer should have tried this at least once themself. (See also: [Transpiler](https://en.wikipedia.org/wiki/Source-to-source_compiler), [Quine](https://en.wikipedia.org/wiki/Quine_(computing)), [LLVM](https://llvm.org/), etc.) Well, this is just my own approach at that. And I am having fun.

This project is in no way intended for any productive use. It's food for thought. An elaborate toy. Art and fart.

Have fun with it and don't hurt your brain.

//HotKey

![Polymorphism](https://raw.githubusercontent.com/hotkeymuc/haul3/master/media/build_polymorphic.gif "Polymorphism")

## Features and Limitations
* This version can not *yet* translate its own source, but it's getting very close. At the moment there are quite some "pythonic" statements used in the parser; so they either have to be eliminated *or* implemented in the language parser as well... In the meantime, feel free to throw other source code at it.
* Finally, HAUL3 is using a proper AST structure, which allows output languages that vastly differ from scripting languages, e.g. JSON or Assembly.
* The source language is now valid (subset of) Python, eliminating the "chicken-egg-problem" of the previous versions. No more bootstrapping needed.
* This is the most object-oriented approach yet. Much easier to comprehend than the previous versions, but also much more complex and powerful. Finally: Real classes, namespaces, imports, libraries, ...
* + Pro: Pretty easy to add new output languages and features.
* - Con: High memory consumption (keeps a lot of structures in RAM), so it may be hard to run a big compilation on a C64...
* HAUL3 adds the concept of "builders". A builder can translate code into another language and package it for a certain hardware platform. This means, for example, one-click deployment to a PalmOS device :-)

## Stupid Name
Initially, the language was called "HAL", which stood for *HotKey's Average Language* and, of course, paid tribune to the computer in [2001: A Space Odyssey](https://en.wikipedia.org/wiki/2001:_A_Space_Odyssey_(film)), as it also was a system that was seemingly running *everywhere*.
But after a while I found that to be just too cheesy. Also, "HAL" [is also something completely different already](https://en.wikipedia.org/wiki/HAL_(software)).

With version 3 I changed to "HAUL" which should create the mental image of *hauling blocks of code to a different place*.

While the language of the old versions were "average" by design, meaning that the language reflects the average functionality of all languages they can translate to, this is not true with version 3 any more.
So I changed it to "amphibious", which stems from the two-fold nature of the source code being a runnable program and a blueprint at the same time. Also, it sounds nice and wacky.

## History
* This third version was started in early 2013 after feeling the need for a real AST structure
* It is based on [HAUL2](https://github.com/hotkeymuc/haul2) which did not use a dedicated lexer/parser/AST. It was therefore much simpler and limited.
* If you are curious for the origins of this project, then have a look at the nasty PHP based first version [HAUL1](https://github.com/hotkeymuc/haul1).

## Usage
* Write your code in HAUL3 (which is valid python). You may need to annotate types where inference is not possible. Use either Python3 style colons or `#@var NAME TYPE` annotations for that. The latter ensures Python 2 compatibility.
* Use `translate.py` to translate code into the desired target language.
* Use `ide.py` to play around with different languages (requires wx).
* Use `build.py` to also compile/bundle/package/test the file on different architectures. This, unfortunately, requires external tools (QEMU, gcc, SDKs), which I regard a bit like cheating.

![HAUL IDE](https://raw.githubusercontent.com/hotkeymuc/haul3/master/media/ide_screenshot000.png "HAUL IDE")

## Directory Structure
* **haul** holds the main source code, including the parser(s) and builders
* **data** holds language/platform specific data, e.g. native libraries or resources
* **examples** holds some example code, ready to be translated to any other language
* **tools** holds external tools that are needed for some builders, e.g. emulators, compilers and SDKs
