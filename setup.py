from setuptools import setup

setup(
    name='Easier68k',
    version='0.0.1',
    url='https://github.com/Chris-Johnston/Easier68k',
    author='Chris Johnston et al',
    author_email='githubchrisjohnston@gmail.com',
    license='MIT',
    packages=['src.easier68k', 'src.easier68k.core', 'src.easier68k.simulator', 'src.easier68k.core.enum', 'src.easier68k.core.util', 'src.easier68k.core.models'],
    setup_requires=['pytest-runner'],
    test_suite='tests.run_test_suite',
    install_requires=['pytest'],
    python_requires='>=3'
)
