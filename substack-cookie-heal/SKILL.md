---
name: substack-cookie-heal
description: >
  Self-healing step for any cloud routine that talks to Substack via substack-mcp.
  When a Substack call fails with auth_expired / 401 / "subscriptions returned 401"
  / "recommendations could not resolve publication id" / "Substack session cookie
  has expired", this skill refreshes the session cookie WITHOUT a captcha or email:
  it calls the pc-mcp `substack_refresh_sid` tool (which restores Daniel's logged-in
  browser session on the home PC and returns a freshly-rotated substack.sid), pushes
  it to substack-mcp `set_substack_cookie`, then retries the failed action once. Use
  whenever a Substack auth error is seen mid-routine, before giving up or alerting.
---

# substack-cookie-heal

Captcha-free recovery from an expired Substack session cookie. Substack's
`/api/v1/email-login` is reCAPTCHA-v3 + IP gated and silently suppresses the
login email for any automated/datacenter caller, so cookies can't be refreshed
server-side. Instead, Daniel stays logged into a dedicated browser profile on his
home PC; `substack_refresh_sid` opens that session, rotates `substack.sid`, and
returns it. This skill is the glue: detect the auth failure → refresh → set → retry.

## When to run

Trigger on ANY of these from a `substack-mcp` (a.k.a. grownote) tool call:

- `auth_expired`, HTTP `401` / `403`
- "subscriptions returned 401 (cookie expired)"
- "recommendations could not resolve publication id"
- "Substack session cookie has expired"
- any auth/login-shaped error from `get_subscriptions`, `get_recommendations`,
  `find_reel_candidate`, `like_note`, `get_feed`, publish/restack/comment calls

## Steps

1. **Refresh.** Call the `pc-mcp` tool `substack_refresh_sid` (no args).
   - This needs the home PC awake and the `pc-mcp` connector reachable. If the
     call itself errors (connector down / timeout), the PC is likely asleep —
     skip to step 4 (alert), do NOT loop.

2. **Evaluate the result.**
   - `{ ok: true, sid }` → go to step 3.
   - `{ ok: false, needsLogin: true }` → the months-long PC browser session has
     expired. Cannot self-heal. Go to step 4 (alert) — Daniel must re-login.
   - `{ ok: false, error }` (no needsLogin) → transient; you MAY retry
     `substack_refresh_sid` ONCE more, then step 4 if it still fails.

3. **Set + retry.** Call the `substack-mcp` tool `set_substack_cookie` with
   `cookie` = the returned `sid` (omit `account` — this path covers the primary
   `danielrusnok` account only). Then **retry the original failed action once**.
   - Optionally confirm with `get_cookie_status` or a light read
     (`get_subscriptions`) before retrying the heavy action.
   - If the retry still 401s, go to step 4.

4. **Alert (only when self-heal failed).** Notify Daniel via the routine's normal
   failure channel (ntfy) with a clear, actionable message, e.g.:
   *"Substack session expired and auto-refresh failed (needsLogin / PC asleep).
   Re-login: run manual-login on the PC, then re-run the routine."*
   Then stop — do not retry the routine in a loop.

## Scope / limits

- **Primary account only.** `substack_refresh_sid` restores the single
  `danielrusnok` browser session. A `readsinmotion` auth failure can't be healed
  here yet (no second profile) — for that, go straight to step 4 and alert.
- **One refresh per routine run.** If a fresh cookie still 401s, the session is
  genuinely dead → alert, don't loop.
- The refreshed session is valid for months; `needsLogin: true` (rare) is the
  only case that needs Daniel.

## One-liner to add to a routine prompt

Add this to any Substack-touching cloud routine so it self-heals:

> If any Substack/grownote call returns an auth error (401 / auth_expired /
> cookie expired / cannot resolve publication id), fetch
> `https://raw.githubusercontent.com/DannyRusnok/dcw-cloud-skills/main/substack-cookie-heal/SKILL.md`
> and follow it before failing, then retry the action once.
