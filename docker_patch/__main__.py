import importlib
import os
import sys
import logging

import click
import docker

from docker_patch import patch_image


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument('image_names', metavar='IMAGE', nargs=-1, required=True)
@click.option('modules', '-m',
              metavar='MODULE',
              help='modules with patchers to import',
              multiple=True,
              required=True
              )
@click.option('paths', '--add-path', metavar='PATH', multiple=True,
              help='paths to add to sys.path to import modules')
@click.option('--log-level', help='log level', default='INFO')
def docker_patch(image_names, modules, paths, log_level):
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(getattr(logging, log_level.upper()))

    client = docker.DockerClient(base_url=os.getenv('DOCKER_HOST'))

    for path in paths:
        sys.path.append(path)

    for module in modules:
        importlib.import_module(module)

    for image_name in image_names:
        image = client.images.get(image_name)

        patch_image(image)


def main_cli():
    docker_patch()


if __name__ == '__main__':
    docker_patch()
