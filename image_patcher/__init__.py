import typing

import docker


def build_image(client: docker.DockerClient, image_name: str, **kwargs: typing.Dict):
    """build image by arguments and yield the build output

    Args:
        client (docker.DockerClient): client to build the image
        image_name (str): name of the image
        kwargs (typing.Dict): other build options

    Yields:
        str: stdout of the build process
    """

    build_kwargs = {
        'tag': image_name,
        'buildargs': {'base_image': image_name}
    }
    kwargs.update(**kwargs)

    _, generator = client.images.build(**build_kwargs)

    while True:
        try:
            line = next(generator)
            if 'stream' in line:
                yield line['stream'].strip('\n')
        except StopIteration:
            break

class App:
    """App to submit patchers and invoke them"""
    def __init__(self):
        self.patcher_funcs = []

    def patcher(self, func):
        """function decorator for image patch functions

        Returns:
            cls: the input class
        """
        self.patcher_funcs.append(func)
        return func

    def patch(self, client : docker.DockerClient, image_name):
        """patch image using submited patchers

        Args:
            client (docker.DockerClient): client to docker
            image_name ([type]): name of image to patch
        """
        print(f'{len(self.patcher_funcs)} patcher(s) available')
        for func in self.patcher_funcs:
            print(f'build {image_name} with {func.__name__}')
            func(client, image_name)

app = App()
