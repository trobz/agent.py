#!/usr/bin/python3

import typer

from common import run
from enum import Enum
from typing_extensions import Annotated


class Backend(str, Enum):
    codex = 'codex'
    opencode = 'opencode'
    gemini = 'gemini'


class Mode(str, Enum):
    normal = 'normal'
    yolo = 'yolo'


def main(
    instructions: Annotated[str,  typer.Argument(
        help='Instruction to execute, required if instructions file'
            ' is not provided',
    )] = '',
    backend: Backend = Backend.codex,
    mode: Mode = Mode.normal,
    instructions_file: Annotated[str, typer.Option(
        '--instructions-file', '-f',
        help='Instructions file, will override instructions argument,'
            ' required if instructions is not provided',
    )] = '',
    model: Annotated[str, typer.Option(
        '--model', '-m', help='Model to use',
    )] = '',
):
    assert instructions_file or instructions, (
        'Either instructions_file or instructions must be provided.'
    )
    if instructions_file:
        with open(instructions_file, 'r') as file:
            instructions = file.read()
    if backend == 'codex':
        cmd_args = ['codex', '--full-auto']
        if model:
            cmd_args.extend(['--model', model])
        cmd_args.extend(['exec', instructions, '--skip-git-repo-check'])
        if mode == 'yolo':
            cmd_args.append('--dangerously-bypass-approvals-and-sandbox')
        else:
            cmd_args.extend(['--sandbox', 'danger-full-access'])
    elif backend == 'opencode':
        if not model:
            model = 'opencode/grok-code'
        cmd_args = [
            'opencode', '--model', model, 'run', instructions,
        ]
    elif backend == 'gemini':
        cmd_args = ['gemini']
        if model:
            cmd_args.extend(['--model', model])
        if mode == 'yolo':
            cmd_args.append('--yolo')
        else:
            cmd_args.extend(['--approval-mode', 'auto_edit'])
        cmd_args.append(instructions)
    run('.', *cmd_args)


if __name__ == '__main__':
    typer.run(main)
