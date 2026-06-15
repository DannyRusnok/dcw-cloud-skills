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
  ALSO run this when Daniel asks for it manually — including via a Telegram reply
  read with `get_recent_replies` (phrases like "oprav substack cookie", "heal
  substack", "fix substack auth", "refresh substack", "obnov cookie"): just run the
  Steps directly, no prior auth error required.
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

## Manual trigger via Telegram

PC watch sessions read Daniel's Telegram replies with `get_recent_replies`. The
alert he gets for a Substack auth failure is dead-end unless he can act on it from
his phone, so treat an inbound reply as a heal command:

- If a recent reply matches a heal phrase — **"oprav substack cookie"**, "heal
  substack", "fix substack", "refresh substack", "obnov cookie", "heal cookie",
  or any close paraphrase — run the **Steps** below immediately, even with no
  prior auth error in this run. Default account = primary (`danielrusnok`); if he
  names `readsinmotion`, heal that one.
- After healing, reply to Daniel on Telegram (`send_telegram_message`) with the
  outcome: ✅ healed + verified, or ❌ `needsLogin` / PC asleep (he must re-login).
- This is the answer to "how do I fix it from my phone": Daniel writes the phrase,
  the PC session that reads his replies runs this skill.

## Steps

1. **Refresh.** Call the `pc-mcp` tool `substack_refresh_sid`. Pass `account` if
   the failure was on a non-primary account (e.g. `{ "account": "readsinmotion" }`);
   omit it for the primary `danielrusnok` account. Both `danielrusnok` and
   `readsinmotion` have a logged-in PC profile and are healable.
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
   `cookie` = the returned `sid` and the SAME `account` you refreshed (omit for
   primary, or `account: "readsinmotion"`). Then **retry the original failed
   action once** (with the same account).
   - Optionally confirm with `get_cookie_status` or a light read
     (`get_subscriptions`) before retrying the heavy action.
   - If the retry still 401s, go to step 4.

4. **Alert (only when self-heal failed).** Notify Daniel via the routine's normal
   failure channel (ntfy) with a clear, actionable message, e.g.:
   *"Substack session expired and auto-refresh failed (needsLogin / PC asleep).
   Re-login: run manual-login on the PC, then re-run the routine."*
   Then stop — do not retry the routine in a loop.

## Scope / limits

- **Two accounts healable:** `danielrusnok` (primary) and `readsinmotion`, each
  with its own PC profile. Always heal the SAME account that failed. Any other
  account → step 4 (alert).
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
