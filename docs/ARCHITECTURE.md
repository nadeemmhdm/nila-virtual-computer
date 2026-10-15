# Architecture

## Product boundary

Nila Virtual Computer is a browser-accessed computer environment backed by Debian Minimal. The browser supplies the graphical desktop; Linux supplies real processes, files and local services. The AI is an orchestrator operating through policy-enforced tools, not a privileged shell.

## Major layers

### Web Desktop

React + TypeScript + Vite provides desktop icons, windows, taskbar, notifications and application surfaces. The UI is intentionally lightweight: no WebGL requirement, no heavy desktop compositor, and minimal animation.

### API / WebSocket Layer

FastAPI exposes authenticated REST and WebSocket endpoints. REST covers metadata and file/task operations; WebSockets are intended for real terminal PTY streaming, task events, notifications and browser-worker events.

### Task Engine

Each autonomous task owns a lifecycle and workspace. A task moves through QUEUED, PLANNING, PREPARING, RUNNING and VERIFYING before it may become COMPLETED. Failure, pause, permission waiting, interruption and cancellation are explicit states.

### AI Layer

The local model receives compact task context and emits structured actions. The model does not receive direct root authority. Planned runtime: llama.cpp server or subprocess adapter using a small compatible GGUF instruct model.

### Tool Layer

Every actionable operation has a schema. The resolver validates tool name, arguments, path boundaries, permission class and resource budget before dispatch. A trusted registry describes package/executable/source/version/RAM/privilege expectations.

### Security Layer

Policy enforcement is deterministic Python/system logic. Normal tasks are confined to managed roots. Package installation and system changes are delegated to a future narrow privileged helper rather than sudo access for the AI process.

### Persistence

SQLite stores users, sessions, tasks, steps, events, tools, permissions, settings, models, downloads and audit metadata. Large logs/artifacts remain files referenced from SQLite.

## Autonomous execution pipeline

```text
request
  -> interpreter
  -> planner
  -> capability resolver
  -> permission check
  -> resource check
  -> workspace preparation
  -> structured execution
  -> observation
  -> bounded error correction
  -> verifier
  -> report
```

A task is never considered complete only because source code was generated. The verifier must produce evidence when technical verification is possible.

## Low-memory strategy

The 4 GB target drives the architecture:

- one heavy task by default;
- local AI and browser workers have explicit lifecycle controls;
- Playwright/Chromium stays off until needed;
- compact summaries replace full log replay to the model;
- project dependencies stay local;
- resource pressure can block new heavy workers;
- expensive polling is avoided.

## Planned terminal architecture

A real terminal will use a PTY on the backend, authenticated WebSocket transport and xterm.js in the browser. Each session will be tied to a user/task, constrained working directory and process ID. Ctrl+C and resize will be real PTY signals, not simulated output.

## Planned browser architecture

User browsing and AI automation are separated. AI automation starts an isolated Chromium + Playwright worker on demand and terminates it after an idle timeout. Downloads pass source/destination validation and are logged.

## Planned privileged helper

The helper exposes narrowly defined operations such as `install_approved_package(tool_id)` and does not accept arbitrary shell text. It validates a signed/static allowlist, logs every request and executes with minimum necessary privilege.
