all:
	make uninstall
	make clean
	make build
	make install
	make test
build:
	nox -s build
clean:
	rm -rf dist build docker_patch.egg-info .nox .pytest_cache .coverage
install:
	pip install dist/*.whl
uninstall:
	pip uninstall docker-patch -y
test:
	nox -s test
freeze:
	pip freeze > requirements.txt
lint:
	python -m pylint docker_patch --disable=no-value-for-parameter,missing-module-docstring