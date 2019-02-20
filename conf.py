# sourced from http://docs.readthedocs.io/en/latest/getting_started.html#in-markdown

from recommonmark.parser import CommonMarkParser

source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']
