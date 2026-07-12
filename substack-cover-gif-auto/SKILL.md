---
name: substack-cover-gif-auto
description: Gateless headless variant of substack-cover-gif, run by the PC video-worker for queued `cover-gif` jobs. Takes a ready still URL + motion brief, renders a Wan i2v loop on the PC's ComfyUI, builds a seamless ping-pong GIF, uploads it, and patches the article's cover_image_url. No questions, no confirmations — ends with a RESULT_URL: or FAILED: marker. Do NOT invoke by hand for an interactive cover gif (use substack-cover-gif); this one assumes the still already exists and that the worker has serialized GPU access.
---

# substack-cover-gif-auto

Headless port of [[substack-cover-gif]] for the `video_jobs` queue. The PC
worker dispatches `kind: "cover-gif"` jobs here. Because the worker drains the
queue **one job at a time on the single RTX 3060**, the ComfyUI queue-race that
forces the manual skill to guard with `list_video_jobs` **cannot happen here** —
so there is NO pre-flight guard. That serialization is the whole reason this
queue path exists.

## Invocation contract (from the worker prompt)

The worker passes three values inline:
- `article_id` — UUID of the Article Forge article whose `cover_image_url` to patch.
- `still_url` — public URL (R2) of the source still PNG. Already generated; do NOT call Codex.
- `motion` — subtle motion brief, or the literal `(default ambient glow/flicker)`.

Run fully autonomous. Never ask anything. End the run with exactly one marker:
- success → `RESULT_URL: <gif_url>`
- any failure → `FAILED: <reason>`

## Prerequisites (PC)

- ComfyUI on `http://desktop-smcnedq:8188` (Wan 2.2 i2v 14B + Lightning 4-step). The worker runs ON the PC, so this is local/Tailscale-reachable.
- `python3` with the wan render deps; `ffmpeg` on PATH.
- cwd = the article-forge repo (the worker spawns claude there). `scripts/upload-gif-raw.ts` + `.env.local` (DATABASE_URL) live here.
- Helpers:
  - Wan render: `~/.claude/skills/substack-video-note/wan_render.py`
  - Ping-pong GIF: `~/.claude/skills/substack-cover-gif-auto/make_loop_gif.py` (bundled in this skill dir)

## Steps

1. **Resolve inputs.** Parse `article_id`, `still_url`, `motion` from the prompt. If `article_id` or `still_url` is missing → `FAILED: missing article_id or still_url`.

2. **Download the still:**
   ```bash
   SRC="/tmp/cover-${article_id}-src.png"
   curl -fsSL "$still_url" -o "$SRC" || echo "FAILED: could not download still"
   ```
   Verify `$SRC` exists and is > 20 KB.

3. **Pick the motion prompt.** If `motion` is `(default ambient glow/flicker)` or empty, use the default ambient string:
   ```
   Subtle ambient motion only: faint flickering glow of the screen/monitor, soft flicker of the lamp light, slow drifting dust motes in the light beams. The person stays still, no body or head movement, mouth closed. No camera movement, no zoom, no pan. Loopable, seamless.
   ```
   Otherwise build a motion string from the brief, but always append the stabilisers: `No camera movement, no zoom, no pan. Loopable, seamless. No face morphing.` (Wan over-animates otherwise.)

4. **Wan i2v render** (832×480, ~97f@24fps, ~2–5 min on the RTX 3060):
   ```bash
   python3 ~/.claude/skills/substack-video-note/wan_render.py "$SRC" "cover-${article_id}" "<MOTION>"
   ```
   Capture the `downloaded: <video_path>` line. If no video path → `FAILED: wan render produced no video`.

   **Wait for the render SYNCHRONOUSLY in the foreground** — run `wan_render.py` as a blocking foreground command (it polls ComfyUI internally) and do not return until it prints `downloaded:`. NEVER launch it as a background task and NEVER end your turn to "wait for a background task notification": this is a headless `claude -p` run — the moment the turn ends the process exits, the worker finds no `RESULT_URL:` and flips the job to failed while ComfyUI is still rendering (incident 2026-07-12, job 80e09dda).

5. **Seamless ping-pong GIF** (forward+reverse = no seam, ideal for ambient loops):
   ```bash
   python3 ~/.claude/skills/substack-cover-gif-auto/make_loop_gif.py "<video_path>" "/tmp/cover-${article_id}-loop.gif" 1000
   ```
   Target < ~6 MB. If larger, re-run with a smaller width (800) / lower fps.

6. **Self-review (optional, fast).** Extract one frame (`ffmpeg -i loop.gif -vframes 1 /tmp/chk.png`) and Read it: confirm no face warp / morph. If badly warped, re-render once with a harder negative ("no body movement, mouth closed, no morphing") or fall back to the default ambient motion.

7. **Upload the raw GIF** (NOT upload-png.ts — that re-encodes to JPEG and kills the animation):
   ```bash
   cd "$REPO_DIR" && URL=$(npx tsx scripts/upload-gif-raw.ts "/tmp/cover-${article_id}-loop.gif" | tail -1)
   ```
   `$URL` must be an `https://…r2.dev/…gif`. If empty → `FAILED: gif upload returned no url`.

8. **Patch the cover:**
   ```bash
   DBURL=$(grep "^DATABASE_URL=" "$REPO_DIR/.env.local" | cut -d= -f2-)
   psql "$DBURL" -c "UPDATE articleforge.articles SET cover_image_url='$URL', updated_at=NOW() WHERE id='${article_id}' RETURNING id;"
   ```
   If 0 rows updated → `FAILED: article ${article_id} not found for cover patch`.

9. **Emit marker:** print `RESULT_URL: <gif_url>` on its own line. Nothing else after it.

## Non-goals / rules
- Do NOT generate the still (Codex) — it is provided. If `still_url` is bad, fail; never substitute.
- Do NOT publish, change `status`, or touch `publishedUrl`.
- Do NOT run a `list_video_jobs` guard — the worker already serializes the GPU.
- Do NOT wait for anything via background tasks / "task notifications" — headless `-p` run ends (and the job fails) the moment you end your turn. All waiting = blocking foreground poll loops.
- Publikační výstupy = EN (n/a here, no copy generated).
- GIF cover style follows the still as-is; brand consistency lives in the still (already approved upstream).

## Relationship to manual skill
- [[substack-cover-gif]] (manual, Mac): generates the still via Codex, runs the queue-race guard, direct-renders. Use interactively.
- This auto skill: still is pre-made, no guard, run by the worker. The two share `make_loop_gif.py` (copy bundled here) and `wan_render.py`.
