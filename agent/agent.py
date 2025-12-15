#!/usr/bin/python3

import os
import pathlib
import subprocess
import typer
import yaml

from datetime import datetime
from enum import Enum
from typing_extensions import Annotated

import litellm


class Backend(str, Enum):
    codex = 'codex'
    opencode = 'opencode'
    gemini = 'gemini'
    litellm = 'litellm'


class Mode(str, Enum):
    normal = 'normal'
    yolo = 'yolo'


def run(cwd, *args, **kwargs):
    """Shortcut to run a command in a given directory."""
    kwargs.setdefault("check", True)
    kwargs.setdefault("cwd", cwd)
    return subprocess.run(args, **kwargs)


def run_litellm(instructions, model, base_url, api_key, provider):
    chosen_model = model or 'gpt-3.5-turbo'
    chosen_provider = provider or os.environ.get('LITELLM_PROVIDER') or 'openai'
    if '/' not in chosen_model:
        chosen_model = f'{chosen_provider}/{chosen_model}'
    api_base = base_url or os.environ.get('LITELLM_API_BASE')
    api_base = api_base or 'http://localhost:1234/v1'
    key = api_key or os.environ.get('LITELLM_API_KEY')
    response = litellm.completion(
        model=chosen_model,
        messages=[{'role': 'user', 'content': instructions}],
        api_base=api_base,
        api_key=key,
    )
    if not response.choices:
        return
    content = response.choices[0].message['content']
    print(content)


def run_agent(cwd, instructions, backend, mode, model, litellm_base_url, litellm_api_key, litellm_provider):
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
    elif backend == 'litellm':
        run_litellm(
            instructions,
            model,
            litellm_base_url,
            litellm_api_key,
            litellm_provider,
        )
        return
    run(cwd, *cmd_args)


def inject_var(command):
    return command.replace('{module_dir}', '.')


def run_workflow(workflow_dir, workflow, backend, mode, model, litellm_base_url, litellm_api_key, litellm_provider):
    for step in workflow['steps']:
        if step.get('ignore', False):
            continue
        if 'work_dir' in step:
            cwd = inject_var(step['work_dir'])
        else:
            cwd = '.'
        now = datetime.now()
        str_now = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{str_now} Running step', step['name'])
        if 'command' in step:
            command = inject_var(step['command'])
            run(cwd, 'bash', '-lc', command)
        elif 'instruction' in step:
            error = 0
            if 'condition' in step:
                try:
                    command = inject_var(step['condition'])
                    run(cwd, 'bash', '-lc', command)
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    error = 1
            instruction = step['instruction']
            if 'files' in step:
                instruction += '\n\nHere are files added for context:\n'
                for file_name in step['files']:
                    file = workflow_dir / file_name
                    if not file.exists():
                        print(f'File {file} does not exist.')
                        error = 1
                        continue
                    with open(file, 'r') as f:
                        instruction += f'\n# {file.name}\n```\n'
                        instruction += f.read()
                        instruction += '\n```\n'
            if not error:
                run_agent(
                    cwd,
                    instruction,
                    backend,
                    mode,
                    model,
                    litellm_base_url,
                    litellm_api_key,
                    litellm_provider,
                )


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
    litellm_base_url: Annotated[str, typer.Option(
        '--litellm-base-url',
        envvar='LITELLM_API_BASE',
        help='Base URL for LiteLLM-compatible server (e.g., LM Studio)',
    )] = '',
    litellm_api_key: Annotated[str, typer.Option(
        '--litellm-api-key',
        envvar='LITELLM_API_KEY',
        help='API key to forward to the LiteLLM-compatible server if required',
    )] = '',
    litellm_provider: Annotated[str, typer.Option(
        '--litellm-provider',
        envvar='LITELLM_PROVIDER',
        help='LiteLLM provider prefix (e.g., openai, ollama, together)',
    )] = '',
):
    assert instructions_file or instructions or workflow, (
        'Either instructions_file or instructions or workflow must be provided.'
    )
    if workflow:
        workflow_dir = pathlib.Path(workflow).expanduser().resolve().parent
        with open(workflow, 'r') as file:
            workflow = yaml.safe_load(file)[0]
        run_workflow(
            workflow_dir,
            workflow,
            backend,
            mode,
            model,
            litellm_base_url,
            litellm_api_key,
            litellm_provider,
        )
    else:
        if instructions_file:
            with open(instructions_file, 'r') as file:
                instructions = file.read()
        run_agent(
            '.',
            instructions,
            backend,
            mode,
            model,
            litellm_base_url,
            litellm_api_key,
            litellm_provider,
        )


def cli():
    typer.run(main)


if __name__ == '__main__':
    cli()
