import logging
import uuid

import docker
import docker.errors

import pytest

from docker_patch import patch_image, register_patcher
from . import data

client = docker.DockerClient()
test_solution = str(uuid.uuid4())

TEST_SOLUTION_FILEPATH = '/test_solution.txt'

logger = logging.getLogger(__name__)

logger.info('test solution: "%s"', test_solution)


# register new patcher
@register_patcher
def patcher(container):
    logger.info('Injecting solution "%s" into container "%s"', test_solution, container)
    r = container.exec_run(f'/bin/sh -c \'echo "{test_solution}" >> {TEST_SOLUTION_FILEPATH}\'')
    if r.exit_code != 0:
        assert False


def on_error(error):
    logger.error('patcher raised error: "%s"', str(error))
    assert False


@pytest.mark.parametrize('image_name', data.images)
def test_package(image_name: str):
    logger.info('Test image: "%s"', image_name)

    try:
        logger.info('Trying remove image first if exists')
        client.images.remove(image_name, force=True)
        logger.info('Image removed successfully')
    except docker.errors.ImageNotFound:
        logger.info('Image does not exists')

    logger.info('Pulling image "%s"', image_name)
    image = client.images.pull(image_name)
    logger.info('Pulling result: "%s"', image)
    assert image
    logger.info('Image ID: "%s"', image.id)

    # store all images original configs
    original_configs = client.api.inspect_image(image.id)['Config']
    logger.info('Original image configs: "%s"', original_configs)

    # patch image
    logger.info('Patching image...')
    new_image = patch_image(image, on_patcher_error=on_error)
    logger.info('New image id: "%s"', new_image.id)

    # test new image
    # check original config equals to patched config
    current_configs = client.api.inspect_image(new_image.id)['Config']
    logger.info('New image configs: "%s"', current_configs)

    def compare_config(key):
        orig_val = original_configs.get(key)
        curr_val = current_configs.get(key)

        return orig_val == curr_val or (orig_val is None and curr_val in ['', []])

    for key in ['Cmd', 'Entrypoint']:
        logger.info('Compare Config.%s', key)
        assert compare_config(key)

    # check solution exists in image by spawn a new container
    logger.info('Check solution exists in new image')
    solution = client.containers.run(new_image, f'cat {TEST_SOLUTION_FILEPATH}',
                                     remove=True).decode('utf-8').strip()
    assert test_solution == solution
