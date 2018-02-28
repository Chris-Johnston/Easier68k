#!/usr/bin/env bash
find . -iname "*.py" | xargs python -m pylint
python tests/run_doctest.py
if [ $? -eq 0 ]
then
    exit 0
else
    exit 1
fi
pytest
if [ $? -eq 0 ]
then
    exit 0
else
    exit 1
fi
