#!/usr/bin/python3

import typer

from common import run


def main(instructions_file: str, backend: str = 'codex', mode: str = 'normal'):
    with open(instructions_file, 'r') as file:
        instructions = file.read()
    if backend == 'codex':
        cmd_args = [
            'codex', '--full-auto', 'exec', instructions,
            '--skip-git-repo-check', '--sandbox', 'danger-full-access',
        ]
        if mode == 'yolo':
            cmd_args.append('--dangerously-bypass-approvals-and-sandbox')
    elif backend == 'opencode':
        cmd_args = [
            'opencode', '--model', 'opencode/grok-code', 'run', instructions,
        ]
    run('.', *cmd_args)


if __name__ == '__main__':
    typer.run(main)
