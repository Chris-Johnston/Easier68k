# Easier68k

A python package based assmebler, disassembler and simulator of the Motorola 68k CPU Architecture.

### Installation

Easier68k currently targets only Python 3.5 and 3.6. 
Other versions may work, but are not actively supported.

Easier68k is not available as a pip package (yet?) so it must be built from source.

1. Install the requirements:
   
   ```bash
    python -m pip install -r requirements.txt
    python setup.py install
    ```
    
2. Install the package (may require root):
   
   ```bash
    python setup.py install
    ```
    
3. Use the package in your code:
   
    ```bash
    # Code example TODO
    ```
    


### Testing

Running the tests assumes that all the prior installation steps have been run already.
The testing sequence is defined in `test/travis.sh`, but these can be run manually.

Doctests are implemented on most smaller methods and utility functions, and pytests are planned
for the overall functionality.

A list of all modules to test is defined in `test/run_doctest.py`. Update this file when
new doctest-able modules are added to the CI.

This file can be run from the shell using `python test/run_doctest.py`.