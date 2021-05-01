import re
import os

import docker

from image_patcher import app, build_image


@app.patcher
def python_patch(client: docker.DockerClient, image_name: str):
    '''patch python image

    Args:
        client (docker.DockerClient): client to docker
        image_name (str): image to patch

    Returns:
        bool: did patched or skipped
    '''

    python_path = client.containers.run(
        image_name, command='which python', remove=True).decode('utf-8')
    if not python_path:
        print(f'No python in image {image_name}')

    print(f'Start rebuild {image_name}')
    for line in build_image(client, image_name, path=os.path.dirname(__file__)):
        print(line)

    print(f'Done building {image_name}')
