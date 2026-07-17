install:
	python3 -m venv .fly_in
	./.fly_in/bin/pip install --upgrade pip
	./.fly_in/bin/pip install -r requirements.txt

test:
	./.fly_in/bin/pytest -v tests/test_pytest.py

run:
	./.fly_in/bin/python fly.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .flake8_cache -exec rm -rf {} +
	find . -type d -name mazegen.egg-info -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

lint:
	./.fly_in/bin/flake8 --exclude=.fly_in,tests --filename='*.py' .
	./.fly_in/bin/mypy --warn-return-any \
		 --warn-unused-ignores \
		 --ignore-missing-imports \
		 --disallow-untyped-defs \
		 --check-untyped-defs \
		 --exclude '^(venv|\.fly_in|tests)/' .

lint-strict:
	./.fly_in/bin/flake8 --exclude=.fly_in,tests --filename='*.py' .
	./.fly_in/bin/mypy --strict \
		--exclude '^(venv|\.fly_in|env|tests)/' .

debug:
	./.fly_in/bin/python -m pdb fly.py
.PHONY: test clean lint-strict lint run install
.SILENT: