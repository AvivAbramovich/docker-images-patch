import docker
import click.testing

from docker_patch.__main__ import docker_patch
from . import data


def test_cli():
    client = docker.DockerClient()

    args = []

    for image in data.images:
        args.append(image)
        client.images.pull(image)

    for module in data.modules:
        args += ['-m', module]
    for path in data.add_paths:
        args += ['--add-path', path]

    runner = click.testing.CliRunner()
    result = runner.invoke(docker_patch, args)
    assert result.exit_code == 0

    # test new image
    for image in data.images:
        res = client.containers.run(image, 'cat patched.txt', remove=True)
        assert res
