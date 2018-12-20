# install current version of module
# would use setup.py test, but I don't think thats working

python3 setup.py develop --user

# run doctest
cd tests
python3 run_doctest.py
cd ..

python3 tests/run_pytest.py
