# Conversation Integrity Rules

Purpose:
Detect instruction drift and context degradation.

Checks:

1. Project Goal Retention
2. Architecture Retention
3. Database Retention
4. Active Task Retention

When uncertain:

- Do not guess.
- Ask clarifying questions.

Before major refactors:

Summarize:

- Current objective
- Current implementation
- Proposed change
- Risks

If previous decisions are forgotten:

STATUS: CONTEXT DEGRADED

Recommend:

- Create conversation summary
- Start fresh session
- Reload summary