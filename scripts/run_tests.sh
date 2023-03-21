cd ..
rm -rf venv
python3 -m venv venv
./venv/bin/python3 -m pip install --upgrade pip
./venv/bin/python3 -m pip install -r requirements.txt
./venv/bin/python3 -m pip install flake8

echo "--- Run all tests ---"
./venv/bin/python3 -m unittest discover tests -v
echo "--- Check flake8 ---"
./venv/bin/python3 -m flake8 .
echo "--- Done ---"