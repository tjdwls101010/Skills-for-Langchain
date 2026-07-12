## Summary

<!-- What changed and why? -->

## Evidence

<!-- Link the official API source and describe any reproducing probe or failure. -->

## Validation

- [ ] `claude plugin validate .claude-plugin/marketplace.json --strict`
- [ ] `claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict`
- [ ] `python3 scripts/validate_evidence.py`
- [ ] `git diff --check`
- [ ] User documentation and `CHANGELOG.md` are updated when behavior changed.
- [ ] Historical evidence was preserved rather than rewritten.
- [ ] No credentials, personal data, or proprietary source code are included.

## Scope

- [ ] The change is focused on a measured LangChain, LangGraph, Deep Agents, plugin, documentation, or maintenance need.
- [ ] The correction explains the reason, version gate, or failure mode—not just a token replacement.
