import importlib
import os
import typing

import click
import docker

from image_patcher import app


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument('image_name')
@click.option('modules', '-m',
              metavar='MODULE',
              help='modules with patchers to import',
              multiple=True,
              required=True
              )
def image_patch(image_name : str, modules : typing.List[str]):
    """Module's cli interface

    Args:
        image_name (str): image to patch
        modules (typing.List[str]): patchers module to import
    """
    client = docker.DockerClient(base_url=os.getenv('DOCKER_HOST'))

    for module in modules:
        importlib.import_module(module)

    app.patch(client, image_name)


if __name__ == '__main__':
    image_patch()
