# install current version of module
# would use setup.py test, but I don't think thats working

sudo python3 setup.py develop

# run doctest
cd tests
python3 run_doctest.py

python3 run_pytest.py

# back into main dir
cd ..



