# agent.py

This is to run different AI agents.

# Usage

```bash
python agent.py <instruction file name>
```

Run the above command to run the agent with instruction file name and default `codex` agent.

```bash
python agent.py <instruction file name> --backend <agent name>
```

Run the above command to run the agent with instruction file name and agent name. Available agents: `codex`, `opencode`.

```bash
python agent.py <instruction file name> --mode <mode>
```

Run the above command to run the agent with instruction file name and mode. Available modes: `normal`, `yolo`. Mode `yolo` is to run `codex` with `--dangerously-bypass-approvals-and-sandbox` option.
