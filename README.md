# agent.py

This is to run different AI agents.

# Usage

```bash
python agent.py <instructions>
```

Run the above command to run the agent with instructions and default `codex` agent.

```bash
python agent.py --instructions-file <instructions file name>
python agent.py -f <instructions file name>
```

Alternatively run one of the above commands to run the agent with instructions in the file name.

```bash
--backend <agent name>
```

Add the above option to run the agent with agent name. Available agents: `codex`, `opencode`, and `gemini`.

```bash
--mode <mode>
```

Add the above option to run the agent with the mode. Available modes: `normal`, `yolo`. Mode `yolo` is to run `codex` with `--dangerously-bypass-approvals-and-sandbox` option and run `gemini` with `--yolo` option.

```bash
--model
```

Add the above option to use a different model.
