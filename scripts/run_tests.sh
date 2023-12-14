cd ..
echo "--- Install required modules ---"
./venv/bin/python3 -m pip install bs4
./venv/bin/python3 -m pip install flake8
echo "--- Run all tests ---"
./venv/bin/python3 -m unittest discover tests -v
echo "--- Check flake8 ---"
./venv/bin/python3 -m flake8 .
echo "--- Done ---"