# Easier68k [![Build Status](https://travis-ci.org/Chris-Johnston/Easier68k.svg?branch=master)](https://travis-ci.org/Chris-Johnston/Easier68k) [![Discord](https://discordapp.com/api/guilds/435529550756052992/widget.png)](https://discord.gg/MXeTCjY)

Easier68k is a python library that assembles and simulates the Motorola 68k CPU Architecture.

NOTE: Easier68k is currently under heavy production and is not stable.

### dev notes / reference material

http://goldencrystal.free.fr/M68kOpcodes-v2.3.pdf

https://www.nxp.com/files-static/archives/doc/ref_manual/M68000PRM.pdf

### Future Development Roadmap

Currently Easier68k is incomplete and is lacking in some ways that prevent it from being considered
"fully featured".

Some goals for future development are:

 - Complete implementation of 68k opcodes.
    - Complete implementation of everything floating point related.
    - Further development of alternative TRAP interaction. (Including graphics and sounds.)
 - Implementation of accurate clock cycle measurement.
 - Interface development:
    - Development of editor plugins for IDEs. Options considered were Atom and VSCode.
    - Development of GUI and editor software that directly interacts with the core package.
    - Further development of the interactive CLI shell.
    - Development of non-interactive command line tools. (Ones that don't run in a shell.)
 - Simplification of the installation and packaging process, as well as any other quality of life
 enhancements for users wishing to install the software.

Specific tasks for development are found on the Issues tab.

### Motivation

There are very few 68K simulators and assemblers and the ones that exist were all found to be lacking in some areas.
We realized we could do better:
* Easier68k is cross platform.
* Easier68k is built as a modular library so anyone can build a front end for it or integrate a 68k simulation into their project.
* Easier68k has a focus on correctness by using unit tests and integration tests for everything.
* Easier68k is MIT licensed so you can use it however you would like.


### How to Use the CLI

The cli is in the folder "easier68k-cli" which comes in this Github repository.
Go to the easier68k-cli folder in the terminal/command prompt and install the dependencies with
```bash
python -m pip install -r requirements.txt
```

Then run the application with
```bash
python ./cli.py
```

You can now assemble and simulate a file
```
(easier68k) assemble ./file.x68, ./assembled.json
(easier68k) simulate ./assembled.json
(easier68k.simulate) run
(easier68k.simulate) exit
(easier68k) exit
```

See the readme in the easier68k-cli for complete documentation.

### Installation

Easier68k currently targets only Python 3.5 and 3.6. 
Other versions may work, but are not actively supported.

See [Easier68k-SampleProject][sampleproject] as an example of incorporating this
package into your code.

1. Add to your `requirements.txt` and install:
   
   ```bash
   # Add this repo to your project's requirements.txt (create one if it doesn't)
   echo git+https://github.com/Chris-Johnston/Easier68k >> requirements.txt
   
   # (re-)install your project requirements (you may want to include the --upgrade flag)
   python -m pip install -r requirements.txt
   ```
    
2. Use the package in your code:
    
    ```python
    import easier68k
    sim = easier68k.simulator.m68k.M68K()
    # you can now use the package!
    ```
    
### Testing

All of the tests can be run with the script `./.testingScript.sh`.
This will install the development version of the package locally and run all of the tests.

Doctests are implemented on most smaller methods and utility functions, and pytests are planned
for the overall functionality.

A list of all modules to test is defined in `tests/run_doctest.py`. Update this file when
new doctest-able modules are added to the CI.

This file can be run from the shell using `python tests/run_doctest.py`.


### License

Easier68k is under the MIT license.


[sampleproject]: https://github.com/Chris-Johnston/Easier68k-SampleProject
