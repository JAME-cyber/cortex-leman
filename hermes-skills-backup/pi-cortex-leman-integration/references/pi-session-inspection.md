# Pi Session Inspection from Hermes

Pi and Hermes run as separate processes with isolated conversation contexts.
However, Pi stores its session history as JSONL files on disk, which Hermes
can read to reconstruct what was discussed in a Pi session.

## When to use

- User asks "can you see my Pi session?" or "what was I working on in Pi?"
- User switches between Pi and Hermes mid-task and wants continuity
- You need context from a Pi session to continue work in Hermes

## Pi session file location

```
~/.pi/agent/sessions/<encoded-project-path>/<ISO-timestamp>_<uuid>.jsonl
```

The project path is the working directory with `/` replaced by `--`.
Examples:
- `/home/tars` → `--home-tars--`
- `/home/tars/cortex-leman-pi-package` → `--home-tars-cortex-leman-pi-package--`
- `/home/tars/.feynman` → `--home-tars-.feynman--`

## Finding the most recent session

```bash
ls -lt ~/.pi/agent/sessions/--home-tars--/*.jsonl | head -5
```

Files are modified in real-time as Pi works, so `ls -lt` gives you the
active or most recent session even if Pi is still running.

## JSONL message format

Each line is a JSON object with this structure:

```json
{
  "type": "message",
  "id": "hex-id",
  "parentId": "hex-id",
  "timestamp": "ISO-8601",
  "message": {
    "role": "user|assistant|toolResult",
    "content": [
      {"type": "thinking", "thinking": "..."},
      {"type": "text", "text": "..."},
      {"type": "toolUse", "toolName": "bash", "input": {...}}
    ]
  }
}
```

Key content types inside `content[]`:
- `thinking` — model's internal reasoning (most valuable for understanding intent)
- `text` — visible output
- `toolUse` — tool calls (bash, file reads, etc.)
- `toolResult` (in `toolResult` role messages) — tool output

## Reading sessions

Pi JSONL lines can be very long (thinking blocks, tool output). Use
`read_file` with offset/limit rather than cat to avoid flooding context.

```python
# Extract role + short content preview from last N lines
import json

with open(session_path) as f:
    lines = f.readlines()

for line in lines[-10:]:
    msg = json.loads(line.strip())
    m = msg.get("message", {})
    role = m.get("role", "?")
    content = m.get("content", [])
    if isinstance(content, list):
        for block in content:
            if block.get("type") == "thinking":
                print(f"[{role}/thinking] {block['thinking'][:300]}")
            elif block.get("type") == "text":
                print(f"[{role}] {block['text'][:300]}")
    elif isinstance(content, str):
        print(f"[{role}] {content[:300]}")
```

## Checking if Pi is running

```bash
ps aux | grep -w "pi" | grep -v grep
# PID, start date, CPU/mem usage
```

Pi runs as a long-lived process. Check the PID start time to know how long
the session has been active.

## Limitations

- **Read-only**: Hermes cannot send messages to Pi or influence its execution.
- **No real-time stream**: You see the on-disk state, which may lag by a few
  seconds behind the live conversation.
- **Large files**: Active sessions can exceed 1MB. Always use pagination.
- **Thinking blocks**: Pi's thinking content is included in the JSONL — this
  is the richest source of context for understanding user intent.
- **Encoded paths**: Project directories with special characters may encode
  differently. List `~/.pi/agent/sessions/` to find the right folder.

## Cross-tool continuity pattern

When the user moves work between Pi and Hermes:

1. Read the most recent Pi session JSONL to understand current state.
2. Extract the last assistant thinking block — it usually contains a plan
   or synthesis that reveals where the work stands.
3. Summarize: "Here's what your Pi session was doing" → then propose
   continuing in Hermes or coordinating between both.
