# agent.py

This is to run different AI agents.

# Installation

```bash
uv pip install git+https://github.com/trobz/agent.py
```

# Usage

```bash
agent <instructions>
```

Run the above command to run the agent with instructions and default `codex` agent.

```bash
agent --instructions-file <instructions file name>
agent -f <instructions file name>
```

Alternatively run one of the above commands to run the agent with instructions in the file name.

```bash
agent --workflow <workflow file name>
agent -w <workflow file name>
```

Or one of the above command can be ran to run the agent with multiple instructions in workflow file name. The format of the workflow file is as follows:

```yaml
- name: name of the work flow
  code: code of the work flow
  steps:
    - name: name of the step
      original: original instruction
      work_dir: optionally work directory
      command: bash command to run
    - name: name of other step
      original: original instruction
      condition: bash command to run and check the return code
      instruction: instruction to run the agent
    - name: name of other step
      original: original instruction
      ignore: true
      notes: notes
```

```bash
--backend <agent name>
```

Add the above option to run the agent with agent name. Available agents: `codex`, `opencode`, `gemini`, and `litellm`.

When using `--backend litellm`, the tool will call a LiteLLM-compatible HTTP endpoint (e.g., LM Studio). You can pass a custom base URL or API key either via flags or environment variables:

```bash
agent --backend litellm --model <model name> --litellm-provider openai --litellm-base-url http://localhost:1234/v1 --litellm-api-key <key-if-needed> "<your instructions>"

# or via env vars
LITELLM_PROVIDER=openai LITELLM_API_BASE=http://localhost:1234/v1 LITELLM_API_KEY=<key-if-needed> agent --backend litellm --model <model name> "<your instructions>"
```

Notes for LM Studio / OpenAI-compatible servers:
- Default provider is `openai` and default model is `gpt-3.5-turbo`. Override `--model` with your served model name and keep the `openai` provider prefix for OpenAI-compatible APIs.

```bash
--mode <mode>
```

Add the above option to run the agent with the mode. Available modes: `normal`, `yolo`. Mode `yolo` is to run `codex` with `--dangerously-bypass-approvals-and-sandbox` option and run `gemini` with `--yolo` option.

```bash
--model
```

Add the above option to use a different model.
