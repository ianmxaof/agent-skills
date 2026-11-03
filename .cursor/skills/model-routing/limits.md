# Subscription Limits Snapshot

> Snapshot taken June 2026. Quotas change often — if a decision hinges on an exact number, re-verify at [cursor.com/help/account-and-billing/pricing](https://cursor.com/help/account-and-billing/pricing) and Anthropic's help center before relying on this file. Update this file when numbers drift.

## Cursor Pro — $20/month

- **$20/mo of included API usage** for manually selected models, billed at provider token rates. Resets on the billing date; unused credit does not roll over.
- **Auto** is a model router with generous included usage, billed at flat discounted rates ($1.25/M input, $6.00/M output, $0.25/M cache read). Treat it as the free-tier workhorse.
- **Premium** router picks the most capable model and bills at that model's API rate — drains the pool fast; treat like a named frontier model.
- Max Mode bills at the model's full API rate.
- When the $20 pool is exhausted: Auto keeps working; named models stop unless on-demand (pay-as-you-go) billing is enabled.
- Check usage: cursor.com/dashboard → Usage.

## Claude Pro — $20/month (includes Claude Code)

- **Dual limit**: rolling 5-hour window + weekly cap shared across claude.ai chat and Claude Code.
- Post May 6, 2026: 5-hour limits **doubled** (~90 prompts/window on Pro, roughly) and peak-hour throttling removed. May 13, 2026: weekly cap +50%, **temporary through ~July 13, 2026** unless extended.
- Weekly capacity ballpark: ~40–80 Sonnet-hours/week on Pro.
- **Sonnet-class models only** on Pro — no Opus in Claude Code at this tier.
- Hitting the 5-hour window → locked out until it rolls; hitting the weekly cap → locked out until the 7-day reset. Budget multi-day grinds accordingly.
- Check usage: `/usage` inside Claude Code (also attributes usage to skills/subagents/MCP servers); `/usage-credits` to set a spend cap on overage credits.

## Practical Implications

- Frontier-model tokens in Cursor are the scarcest resource (~$20/mo). Spend them on *judgment* (planning, review, debugging), not *volume* (code emission).
- Claude Code is a second, independent compute budget. Using it for grindy work effectively doubles available agent time at no marginal cost — as long as the weekly cap survives.
- Auto in Cursor is the abundant resource. Default everything there.
