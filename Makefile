freeze:
	pip freeze > requirements.txt
lint:
	python -m pylint image_patcher --disable=no-value-for-parameter,missing-module-docstring