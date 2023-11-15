cd ..
echo "--- Run all tests ---"
./venv/bin/python3 -m unittest discover tests -v
echo "--- Check flake8 ---"
./venv/bin/python3 -m flake8 .
echo "--- Done ---"