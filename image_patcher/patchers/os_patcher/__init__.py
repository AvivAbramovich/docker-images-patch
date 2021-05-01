import re
import os

import docker

from image_patcher import app, build_image

OS_ALPINE = 'Alpine'
OS_UUBUNTU = 'Ubuntu'
OS_DEBIAN = 'Debian'
OS_CENTOS = 'CentOS'

def _obtain_os(os_name):
    if 'Alpine Linux' in os_name:
        return OS_ALPINE
    if 'Ubuntu' in os_name:
        return OS_UUBUNTU
    if 'Debian' in os_name:
        return OS_DEBIAN
    if 'CentOS' in os_name:
        return OS_CENTOS
    raise Exception('Failed to obtain OS')

@app.patcher
def linux_os_patch(client: docker.DockerClient, image_name: str):
    '''Patch linux images by their specific os'''
    os_release = client.containers.run(
        image_name, command='cat /etc/os-release', remove=True).decode('utf-8')
    matches = re.findall(r'NAME=\"([a-zA-Z ]+)\"', os_release)
    if not matches:
        raise Exception('Failed to find NAME line in /etc/os-release')
    os_name = matches[0]
    os_name = _obtain_os(os_name)

    print(f'"{image_name}" os is "{os_name}"')

    context_path = os.path.join(
        os.path.dirname(__file__), 'contexts', os_name)
    print(f'Context path: "{context_path}"')

    print(f'Start rebuild {image_name}')
    for line in build_image(client, image_name, path=context_path):
        print(line)

    print(f'Done building {image_name}')
