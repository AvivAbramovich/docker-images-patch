import typing
import logging

import docker
from docker.models.images import Image
from docker.models.containers import Container

registered_patchers: typing.List[typing.Callable] = []


__version__ = '0.1.2'


def default_on_error(error: Exception):
    raise error


def _get(d: dict, key: str, default):
    res = d.get(key, default)
    return default if res is None else res


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

    # create a container
    logger.info('Creating container for "%s"', image)
    container: Container = client.containers.run(
        image, detach=True, entrypoint='/bin/sh',
        remove=True, tty=True, network_mode='host'
    )
    logger.info('Container: "%s" (id: "%s")', container.name, container.id)

    try:
        for patch_func in registered_patchers:
            try:
                logger.info('calling patcher func "%s"', patch_func.__name__)
                patch_func(container)
            except Exception as error:
                on_patcher_error(error)

        # commit
        logger.info('Commit container')
        result_image = container.commit(conf={
            'Entrypoint': _get(orig_config, 'Entrypoint', []),
            'Cmd': _get(orig_config, 'Cmd', [])
        })

        logger.info('New image id: "%s"', result_image.id)

        # re-tag
        logger.info('tag new image with %d tags', len(image.tags))
        for tag in image.tags:
            logger.info('-tag "%s"', tag)
            result_image.tag(tag)

        # fetch image again with tags
        return client.images.get(result_image.id)
    finally:
        # fetch the updated container object
        container = client.containers.get(container.id)
        if container.status == 'running':
            # stop container (should be removed)
            logger.info('Stopping container "%s"', container.name)
            container.stop()
