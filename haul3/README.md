#HAUL3
(HotKey's Amphibious Universal Language)

This is a puzzle I have set up for myself: Can I write a program that translates itself into other languages? Nothing new, nothing special. Every programmer should have tried this at least once. Well, this is my approach at that.

So I tried. And it worked. And it was fun.

So I did it again. And it was even more fun.

So I did it a third time. And now I really like it. :-)

This is in no way intended for any productive use. It's food for thought. An elaborate toy. Art and fart.
Have fun with it and don't hurt your brain.

//HotKey


#Version 3 (2013-01 - now):
* Finally, I am using a proper AST structure (modules, functions, expressions, instructions, ...)
* Just doing it the way everyone else does it: Lex it, parse it, generate output. Boring, yet powerful. Now, translation to binary output is finally feasible.
* This is the most OOP approach yet. Much easier to comprehend than the previous versions, which streamed the tokens on-the-fly.
* The source language "HAL3" is now just valid python, eliminating the "chicken-egg-problem" of the previous versions.
* No boot strapping is needed any more, since all parts of the source are runnable.
* Pro: Pretty easy to add a new output language
* Con: High memory consumption (keeps the whole AST structure in RAM), so it may get hard to create a C64 output module.

#Usage
* Write your code in HAL3 (which is valid python). You may need to add variable types in some places. Use either Python3 colons or "#@var NAME TYPE" comments for that.
* Use translate.py to translate that file into the desired target language.
* Use ide.py to play around with different languages
* Use build.py to also compile/bundle/package/test the file on different architectures. This, unfortunately, requires external tools (QEMU, gcc, SDKs), which I regard as cheating.

#Directory Structure
* haul holds the main source code, including the parser(s) and builders
* data holds language/platform specific data, e.g. native libraries or resources
* examples holds some example code, ready to be translated to any other language
* tools holds external tools that are needed for some builders, e.g. emulators, compilers and SDKs
