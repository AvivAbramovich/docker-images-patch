# Docker-Patch

Patch docker images to fit your purposes and organization requirements

## Installation

```bash
pip install docker-patch
```

## Usage

Add your own patch function like this:

```python
import docker_patch

@docker_patch.register_patcher
def patcher_func(container):
    print(f'patch container "{container}"')

    container.exec_run('/bin/sh -c "echo \"hi from patch function!\" >> patched.txt"')
```

You can register multiple patchers, and then use it in one of these options:

### cli

```bash
docker-patch <IMAGE_NAME> -m <module_name>
```

You can add additional `-m <module>` as you like and make a patchers chain that work on your image (in order of appearance).
If you would like to import a module that not in your current path or installed in the interpreter libraries, you can add `--add-path` like this:

```bash
# assume my_patcher is in /path/to/my_patcher.py
docker-patch <IMAGE_NAME> -m my_patcher --add-path /path/to
```

This will add `/path/to` to `sys.path` so the patcher can import the `my_module`

### In code

Use it directly from code

```python
import docker
import docker_patch

# assume you registered patchers as shown above
client = docker.DockerClient()
image = client.images.get('some-image')

result_image = docker_patch.patch_image(image)
```