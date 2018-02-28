from setuptools import setup, find_packages

setup(
    name='easier68k',
    version='0.0.1',
    url='https://github.com/Chris-Johnston/Easier68k',
    author='Chris Johnston et al',
    author_email='githubchrisjohnston@gmail.com',
    license='MIT',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    python_requires='>=3'
)

print('done')
