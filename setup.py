from setuptools import setup

setup(
    name='Easier68k',
    version='0.0.1',
    url='https://github.com/Chris-Johnston/Easier68k',
    author='Chris Johnston et al',
    author_email='githubchrisjohnston@gmail.com',
    license='MIT',
    packages=['src.easier68k', 'src.easier68k.core', 'src.easier68k.simulator', 'src.easier68k.core.enum', 'src.easier68k.core.util', 'src.easier68k.core.models'],
    zip_safe=False,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'python tests/run_doctest.py'],
    install_requires=['pytest']
)
