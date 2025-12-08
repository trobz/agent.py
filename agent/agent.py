#!/usr/bin/python3

import subprocess
import typer
import yaml

from enum import Enum
from typing_extensions import Annotated


class Backend(str, Enum):
    codex = 'codex'
    opencode = 'opencode'
    gemini = 'gemini'


class Mode(str, Enum):
    normal = 'normal'
    yolo = 'yolo'


def run(cwd, *args, **kwargs):
    """Shortcut to run a command in a given directory."""
    kwargs.setdefault("check", True)
    kwargs.setdefault("cwd", cwd)
    return subprocess.run(args, **kwargs)


def run_agent(cwd, instructions, backend, mode, model):
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
    run(cwd, *cmd_args)


def run_workflow(workflow, backend, mode, model):
    for step in workflow['steps']:
        if step.get('ignore', False):
            continue
        if 'work_dir' in step:
            cwd = step['work_dir'].replace('{module_dir}', '.')
        else:
            cwd = '.'
        print('Running step', step['name'])
        if 'command' in step:
            run(cwd, 'bash', '-lc', step['command'])
        elif 'instruction' in step:
            error = 0
            if 'condition' in step:
                try:
                    run(cwd, 'bash', '-lc', step['condition'])
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    error = 1
            if not error:
                run_agent(cwd, step['instruction'], backend, mode, model)


def main(
    instructions: Annotated[str,  typer.Argument(
        help='Instruction to execute, required if instructions file'
            ' or workflow is not provided',
    )] = '',
    backend: Backend = Backend.codex,
    mode: Mode = Mode.normal,
    instructions_file: Annotated[str, typer.Option(
        '--instructions-file', '-f',
        help='Instructions file, will override instructions argument,'
            ' required if instructions or workflow is not provided',
    )] = '',
    model: Annotated[str, typer.Option(
        '--model', '-m', help='Model to use',
    )] = '',
    workflow: Annotated[str, typer.Option(
        '--workflow', '-w',
        help='Workflow to use, required if instructions_file or'
            ' instructions is not provided, will override instructions'
            ' or instructions_file',
    )] = '',
):
    assert instructions_file or instructions or workflow, (
        'Either instructions_file or instructions or workflow must be provided.'
    )
    if workflow:
        with open(workflow, 'r') as file:
            workflow = yaml.safe_load(file)[0]
        run_workflow(workflow, backend, mode, model)
    else:
        if instructions_file:
            with open(instructions_file, 'r') as file:
                instructions = file.read()
        run_agent('.', instructions, backend, mode, model)


def cli():
    typer.run(main)


if __name__ == '__main__':
    cli()
