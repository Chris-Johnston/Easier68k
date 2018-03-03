# install current version of module
# would use setup.py test, but I don't think thats working
cd src
sudo python3 setup.py install
cd ..

# run doctest
cd tests
python3 run_doctest.py

python3 run_pytest.py

# back into main dir
cd ..



