import logging

import docker
import click.testing

from docker_patch.__main__ import docker_patch
from . import data


def test_cli():
    logger = logging.getLogger('test_cli')

    client = docker.DockerClient()

    args = []

    logger.info('Add %d images...', len(data.images))
    for image in data.images:
        args.append(image)
        try:
            logger.info('Trying remove image first if exists')
            client.images.remove(image, force=True)
            logger.info('Image "%s" removed successfully', image)
        except docker.errors.ImageNotFound:
            logger.info('Image "%s" does not exists', image)

        logger.info('Pulling "%s"', image)
        image = client.images.pull(image)
        logger.info('Pulled "%s" (id: "%s")', image, image.id)

    for module in data.modules:
        logger.info('Add module "%s"', module)
        args += ['-m', module]
    for path in data.add_paths:
        logger.info('Add path "%s"', path)
        args += ['--add-path', path]

    logger.info('Cli args: "%s"', args)

    runner = click.testing.CliRunner()
    result = runner.invoke(docker_patch, args)
    logger.info('exit code: %d', result.exit_code)
    assert result.exit_code == 0

    # test new image
    logger.info('Test %d images...', len(data.images))
    for image in data.images:
        logger.info('Test image "%s"', image)
        res = client.containers.run(image, 'cat patched.txt', remove=True)
        logger.info('Result: "%s"', res)
        assert res
