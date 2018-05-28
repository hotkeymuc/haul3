SR1/HAL1 (2011-07 - 2012-03):
	= "Flat" translation: no lexer, compiler - just a simple text-translator
	= First word in each line is always the command, then tab separated parameters
	= Written in PHP :-(
	+ Some kind of structure/state while parsing (instructions, expressions, ...), but no "understanding" of the code
	+ OOP (HTKs are classes)
	+ Sample Code: "shadowRunner" - a small VM
	+ "HYBERnation" - Programs can store their state across translations!
	+ Goodie: SR1 can convert HAL to shadowRunner byte code!!! YO DAWG!!! Recursion galore! The system can translate itself to a language it can interpret itself... wow.
	! Works great for what it does!!!
	= 600 lines (12kb) per output kernel
	- Language is really ugly (an "assembler php hate child") - no nested expressions, looks repetitive
	- Needs a boot-strapper to initially translate itself to an executable language (translateOnce.php)
	- limited syntax (assembler like - the worst quirks of all output languages combined!)
	- parsing is a bit messy, since we have no syntax tree
	- Can only output languages that are similar in their syntactic structure (PHP, Python, JS, VBS, ...)
	-> Maybe some sort of syntax tree is not bad after all... Especially for binary output.


Usage
* Write your code in HAL (see src.hal for examples)
* Pick an output language (JS, PHP, VBS, SR), see src.hal/htk_*.hal for a selection
* Translate the HTK for the desired language to your current platform (e.g. by running translateOnce.php or run_deploy.php). Oh, create "src.gen" and "deploy" directories first.
* Run the HTK to convert your source HAL file to the desired language