import subprocess


def run(cwd, *args, **kwargs):
    """Shortcut to run a command in a given directory."""
    kwargs.setdefault("check", True)
    kwargs.setdefault("cwd", cwd)
    return subprocess.run(args, **kwargs)


def run_read(cwd, *args, **kwargs):
    """Shortcut to run a command in a given directory."""
    return run(cwd, *args, **kwargs, stdout=subprocess.PIPE).stdout.decode("utf-8")
