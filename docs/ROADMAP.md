# Development Roadmap

The platform is intentionally built phase-by-phase. Each phase must leave the repository runnable and testable.

## Phase 1 — Foundation

Status: in repository.

- FastAPI backend
- configuration boundaries
- health/resource APIs
- controlled filesystem primitives
- task state machine
- isolated workspace manager
- trusted tool registry model
- browser desktop shell
- installer/update/uninstall/diagnostics scripts
- core docs/tests

## Phase 2 — Core Computer

Next priorities:

- authenticated user/session model
- SQLite migrations and persistent tasks
- xterm.js terminal
- PTY WebSocket backend
- Ctrl+C / resize / process termination
- richer File Manager: create, rename, move, copy, upload, download, preview, metadata, search, sorting
- notifications and window-state persistence
- task event WebSocket

## Phase 3 — Local AI

- llama.cpp build/runtime adapter
- small Qwen-family GGUF configuration
- model import/validation/load/unload
- compact system contract
- planner and intent interpreter
- structured action parser
- context summarizer
- bounded retry/error-analysis loop
- evidence-based task reporter

## Phase 4 — Tool Manager

- package/version parser framework
- Debian package discovery
- cached update metadata
- compatibility decisions
- privileged helper with narrow package API
- project-local Python/Node dependency provisioning
- tool install/update audit logging

## Phase 5 — Browser

- normal browser surface
- tabs/history/bookmarks/downloads
- isolated Playwright worker
- browser permission policy
- on-demand Chromium startup and idle shutdown
- structured browser tools

## Phase 6 — Autonomous Tasks

- persistent queue
- one-heavy-task default scheduler
- pause/resume/cancel
- recovery after service restart
- task/project memory
- artifacts and verification evidence
- max automatic correction attempts = 3

## Phase 7 — Security

- production authentication
- secure cookie sessions
- CSRF protection
- WebSocket authentication/origin checks
- rate limiting
- audit redaction
- emergency stop
- security regression tests
- privileged helper review

## Phase 8 — Optimization

- 4 GB profiling
- AI/browser lifecycle tuning
- memory-pressure controller
- compact context policies
- process reaper
- lazy app/service loading
- low-cost UI polling

## Phase 9 — Release

- signed release/update metadata
- migration/rollback policy
- complete CLI
- final diagnostics
- release test matrix
- real resource-usage measurements
- install validation on clean Debian target

## Definition of Done

The final product can only be declared complete after real target-host validation confirms:

1. successful clean install;
2. functional web desktop;
3. real PTY terminal;
4. real controlled file operations;
5. working browser;
6. local AI response through llama.cpp;
7. schema-validated AI tool execution;
8. verified autonomous coding task completion;
9. approved on-demand package installation;
10. permission enforcement;
11. cancellation/recovery/emergency stop;
12. authentication and WebSocket security tests;
13. auto-start after reboot;
14. measured safe behavior on a 4 GB RAM host.
