# Applications

This repository currently has **one application**: the local Conversation
Browser. The scripts in `src/` are private data-pipeline, model-evaluation,
reporting, and safety-review CLIs; they are not independently deployed apps.

| Application | Entry | Purpose |
| --- | --- | --- |
| [Conversation Browser](conversation-browser/README.md) | `src/conversation_browser.py` | Locally browse interim conversations and, after authorized human review, create a constrained text-free flag. |

`apps/` is the application catalog and ownership boundary. Until a reviewed
migration says otherwise, application source remains at its documented
canonical path under `src/`; do not relocate it opportunistically.
