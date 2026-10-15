# Security Model

## Trust boundaries

The browser, AI model output, uploaded files, remote web content, archives and task-generated code are untrusted inputs. Deterministic backend policy code remains authoritative.

## Core rules

1. Never execute free-form LLM text as root.
2. Every AI action must match a structured schema.
3. Every filesystem path must resolve inside an allowed root.
4. Every privileged operation must use a narrow helper API.
5. High-risk and critical actions require explicit approval.
6. Secrets must be redacted from logs.
7. The raw terminal must never be exposed without authentication.
8. Public internet exposure is off by default.

## Allowed roots

Ordinary task work is constrained to managed locations such as:

```text
/var/lib/nila-virtual-computer/workspaces
/home/nila-computer/shared
```

The path layer rejects traversal, unsafe absolute paths and symlink escape.

## Permission classes

### SAFE

Examples: read/write within workspace, create project files, run approved unprivileged commands in the task workspace.

### SENSITIVE

Examples: network access, browser automation, installation of an approved Debian package, access to selected user directories.

### HIGH_RISK

Examples: firewall changes, OS configuration, user/account changes, mounting disks, exposing a service publicly.

Requires explicit confirmation.

### CRITICAL

Examples: reboot/shutdown, destructive disk operations, mass deletion, disabling core security controls.

Requires strong confirmation and should support re-authentication.

## Command execution

The intended pipeline is:

```text
structured action
-> schema validation
-> permission decision
-> path validation
-> resource/timeout policy
-> execution as least-privileged service user
-> output capture
-> audit record
-> verification
```

Commands should use bounded timeouts and controlled working directories. Shell interpretation should be avoided where direct argv execution is possible.

## Package installation

The autonomous agent does not own unrestricted sudo credentials. A dedicated helper will accept only approved operations such as installation of a registry-defined Debian package. Random website instructions and patterns such as `curl URL | sh` are forbidden.

## Network controls

Production deployment must add authenticated access, secure session cookies, CSRF protection for state-changing HTTP requests, WebSocket authentication, origin validation and login throttling. Bind locally/private by default.

## Audit logging

Audit records should include timestamp, task, user, initiator, action, tool, command category, affected path, permission decision, result, exit code and duration. Passwords, tokens, authorization headers and other secrets must be redacted.

## Emergency Stop

The planned Emergency Stop disables new autonomous actions, terminates AI-owned browser workers and eligible AI-owned processes, preserves logs and keeps the inspection UI accessible. It must not delete user files merely to stop execution.

## Reporting vulnerabilities

Do not post exploitable security details publicly before a fix is available. Use a private maintainer contact/security reporting channel when one is configured for the repository.
