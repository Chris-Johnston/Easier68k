# Easier68k [![Build Status](https://travis-ci.org/Chris-Johnston/Easier68k.svg?branch=master)](https://travis-ci.org/Chris-Johnston/Easier68k)

A python package based assmebler, disassembler and simulator of the Motorola 68k CPU Architecture.

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