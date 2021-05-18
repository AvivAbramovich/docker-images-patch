import typing
import logging

import docker
from docker.models.images import Image
from docker.models.containers import Container

registered_patchers: typing.List[typing.Callable] = []


__version__ = '0.1'


def default_on_error(e: Exception):
    raise e


def register_patcher(
        patcher_func: typing.Callable[[Container], None]
) -> typing.Callable:
    # TODO: add docstring
    registered_patchers.append(patcher_func)
    return patcher_func


def patch_image(
        image: Image,
        client: docker.DockerClient = None,
        on_patcher_error: typing.Callable[[Exception], None] = None,
        logger: logging.Logger = None
) -> Image:
    # TODO: add dostring
    if not logger:
        logger = logging.getLogger()

    if not client:
        client = image.client
    if not on_patcher_error:
        on_patcher_error = default_on_error

    orig_config = client.api.inspect_image(image.id)['Config']
    orig_entrypoint = orig_config['Entrypoint']
    if not orig_entrypoint:
        orig_entrypoint = ''

    # create a container
    logger.info(f'Creating container for "{image}"')
    c: Container = client.containers.run(
        image, detach=True, entrypoint='/bin/sh',
        remove=True, tty=True, network_mode='host'
    )
    logger.info(f'Container: "{c.name}" (id: {c.id})')

    try:
        for patch_func in registered_patchers:
            try:
                logger.info(f'calling patcher func "{patch_func.__name__}"')
                patch_func(c)
            except Exception as e:
                on_patcher_error(e)

        # commit
        logger.info('Commit container')
        result_image = c.commit(conf={'Entrypoint': orig_entrypoint})

        logger.info(f'New image id: {result_image.id}')

        # re-tag
        logger.info(f'tag new image with {len(image.tags)} tags')
        for tag in image.tags:
            logger.info(f'-tag "{tag}"')
            result_image.tag(tag)

        # fetch image again with tags
        return client.images.get(result_image.id)
    finally:
        # fetch the updated container object
        c = client.containers.get(c.id)
        if c.status == 'running':
            # stop container (should be removed)
            logger.info(f'Stopping container "{c.name}"')
            c.stop()
