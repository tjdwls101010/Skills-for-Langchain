# Security Policy

## Supported versions

Security fixes are provided for the latest published release.

| Version | Supported |
|---|---|
| 1.x | Yes |
| < 1.0 | No |

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could put users at risk.

Use [GitHub private vulnerability reporting](https://github.com/tjdwls101010/Skills-for-Langchain/security/advisories/new). If that channel is unavailable, email `chunghun1@naver.com` with the subject `Skills for LangChain security report`.

Include the affected version, impact, reproduction steps, and any suggested mitigation. You can expect an acknowledgement within 7 days and a status update within 14 days. Timelines for a fix depend on severity and the upstream APIs involved.

## Security boundary

The installed plugin registers knowledge files only. It defines no hooks, MCP servers, executable plugin commands, background monitors, or automatic dependency installation. The repository's maintenance validator under `scripts/` is not registered as a plugin component and is never run automatically for users.

The guidance discusses filesystems, sandboxes, remote execution, permissions, and credentials, but documentation cannot enforce runtime isolation. Users remain responsible for reviewing generated code, pinning dependencies, protecting secrets, configuring least privilege, and testing the actual deployment environment.
