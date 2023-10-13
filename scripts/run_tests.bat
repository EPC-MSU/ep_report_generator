cd ..
echo --- Run all tests ---
venv\Scripts\python -m unittest discover tests -v
echo --- Check flake8 ---
venv\Scripts\python -m flake8 .
echo --- Done ---
pause