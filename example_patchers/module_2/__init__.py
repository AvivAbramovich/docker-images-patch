import logging

from docker_patch import register_patcher


@register_patcher
def patcher_func_2(container):
    logging.info(f'module 2 - Patching {container}')

    r = container.exec_run('/bin/sh -c \'echo "hi from module 2" >> patched.txt\'')
    if r.exit_code != 0:
        raise Exception('command failed')
