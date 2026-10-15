# Nila AI Security Features

Nila uses defense in depth. The model is an untrusted planner; deterministic code remains authoritative.

## Implemented foundation in this phase

- Desktop AI Chat task assignment.
- Permanent STOP AI / resume control.
- Capability controls: files, terminal, network, browser, package install and system settings.
- Safe mode and local-only privacy mode.
- Secret redaction for common key/token/password patterns before chat objectives are stored.
- Append-only JSONL audit events.
- Workspace snapshot foundation for rollback.
- Emergency stop blocks new AI assignments and pauses active in-memory tasks.
- File writes pass the capability and controlled-root policy.
- Cross-platform protected-root and command-risk classification primitives.

## Security features that must gate execution as runtime modules mature

### Action Preview
Before execution show plan, requested capabilities, files, commands, downloads, network targets and risk classification. High-risk/critical actions require explicit confirmation.

### Snapshot and Rollback
Create a snapshot before destructive mutations. Rollback is task-scoped and may never accept arbitrary source paths.

### Task Sandbox
Each autonomous task gets its own workspace, process ownership and resource budget. A task cannot read another task workspace unless explicitly shared.

### Command Risk Engine
Parse commands before execution. Critical disk/system/destructive operations are denied by default. Avoid executing AI-produced shell strings through `shell=True`.

### Protected Files
OS roots, credentials, SSH keys, browser credential stores and secret files remain denied unless a narrow trusted operation explicitly authorizes them.

### Network Policy
Network access is a separate capability. Future fetch/browser implementations must enforce destination policy, block loopback/private-network SSRF by default where applicable, record destinations and respect local-only mode.

### Download Verification
Downloaded executables/packages require trusted-source policy, content type/size checks, hash recording and signature/checksum verification when the publisher provides it.

### Secret Guard
Secrets should be redacted from model prompts, logs and UI. Secret values should eventually use OS credential storage rather than plaintext configuration.

### Trusted Tool Manager
Use an allowlisted registry and OS adapter. The model asks for a logical tool; deterministic code chooses approved winget/APT/project-local installation methods.

### Resource Limits
Per-task CPU/RAM/process/time limits are required before arbitrary task execution is enabled. One heavy task remains the 4 GB default.

### Recovery and Verification
Interrupted tasks become recoverable rather than silently resumed. Completion requires deterministic verification such as exit status, expected artifact checks, tests or health checks.

### Teach Nila
Recorded workflows must store structured approved actions rather than raw privileged shell transcripts. Replays pass through the same permission and risk policy.

## Non-negotiable rule

No LLM output receives unrestricted Administrator/root execution. Every side effect follows:

`plan -> schema -> capability -> risk -> permission -> snapshot -> execute -> audit -> verify -> report`
