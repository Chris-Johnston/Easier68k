from setuptools import setup, find_packages

setup(
    name='easier68k',
    version='0.1.0',
    url='https://github.com/Chris-Johnston/Easier68k',
    author='Adam Krpan, Chris Johnston, Levi Stoddard',
    author_email='githubchrisjohnston@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    setup_requires=['pytest-runner'],
    python_requires='>=3'
)

print('done')
