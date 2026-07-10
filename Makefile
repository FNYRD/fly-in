FILE = test_pytest.py

test:
	pytest -v test_pytest.py


clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .flake8_cache -exec rm -rf {} +
	find . -type d -name mazegen.egg-info -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +

.PHONY: test clean
.SILENT: