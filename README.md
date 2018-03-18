# Easier68k [![Build Status](https://travis-ci.org/Chris-Johnston/Easier68k.svg?branch=master)](https://travis-ci.org/Chris-Johnston/Easier68k)

Easier68k is a python library that assembles to 68k and simulates the Motorola 68k CPU Architecture.
It is built as a library so anyone can create a front end for it. Currently this repository includes a CLI and a GUI is in the works.

NOTE: Easier68k is currently under heavy production and is not stable.

### Motivation

There are very few 68K simulators and assemblers. The only one which is still maintained and complete is Easy68k.
We realized we could do better:
* Easy68k is not cross platform, but Easier68k is
* Easy68k is not modular and enforces you to use its editor and GUI, but Easier68k is built as a modular library so it can fit in anyones personal setup
* Easy68k is buggy, but Easier68k has a focus on correctness by using unit tests and integration tests for everything.
* Easy68k is GPL licensed, but Easier68k is MIT licensed


### How to Use?

If you want to use this as a library to either develop a front end or automate some special tasks then simply import the
package in your project and start coding.

If you want to use this to assemble and simulate some 68k assembly then keep on reading.

Currently there is only one front end available for easier68k which is the easier68k-cli which comes in this Github repository.
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

Running the tests assumes that all the prior installation steps have been run already.
The testing sequence is defined in `tests/travis.sh`, but these can be run manually.

Doctests are implemented on most smaller methods and utility functions, and pytests are planned
for the overall functionality.

A list of all modules to test is defined in `tests/run_doctest.py`. Update this file when
new doctest-able modules are added to the CI.

This file can be run from the shell using `python tests/run_doctest.py`.

[sampleproject]: https://github.com/Chris-Johnston/Easier68k-SampleProject


### License

Easy68k is under the MIT license.