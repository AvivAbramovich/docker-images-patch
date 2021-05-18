import nox


@nox.session(name='test')
def test(session):
    session.install('flake8', 'tox')
    session.run('flake8', '--show-source', '--statistics', 'docker_patch')
    session.run('tox')


@nox.session(name='build')
def build(session):
    session.install('setuptools', 'wheel', 'm2r')
    session.run("python", "setup.py", "sdist", "bdist_wheel")
