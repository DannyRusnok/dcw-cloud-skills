---
name: substack-video-note-auto
description: >
  Autonomous, GATELESS variant of substack-video-note. Runs unattended on
  Daniel's home PC (RTX 3060), invoked by the video-worker via `claude -p`
  for `kind: video-note` queue jobs. Turns a still image + a 1-2 line quote
  into a ~4s muted-autoplay Substack Note video: download image → Wan 2.2
  i2v Lightning render (832x480, 97f) → ASS quote overlay → R2 upload. No
  human approval steps. Do NOT use interactively — for hands-on note videos
  use the original `substack-video-note` skill.
---

# substack-video-note-auto

Gateless autonomous Substack-note-video pipeline. Sister to
`substack-video-note` but with every prompt removed and the input taken from
a queue payload instead of `~/Downloads`. Run by the `video-worker` against a
`video_jobs` row of `kind: video-note`.

## Invocation contract

The worker invokes this skill with three inputs in the prompt:

- `image_url` — public URL of the source still image
- `text` — the 1-2 line quote to overlay
- `accent_word` — optional single word to colour red, or `(none)`

On success: print exactly `RESULT_URL: <r2-mp4-url>` as the last line.
On failure: print exactly `FAILED: <one-line reason>` as the last line.
The worker greps for these. Never end without one of them.

## Operating rules (gateless)

- **Never ask a question. Never wait for approval.** No human is in the loop.
- **Fail loud, fail fast.** On any unrecoverable error print `FAILED: <reason>`.
- All paths below are Windows paths on the home PC.

## Pre-flight (abort with FAILED if any check fails)

1. Article Forge repo at `C:\Users\danie\article-forge` with `.env.local`
   (needs `R2_*`). The R2 upload step runs from there.
2. ComfyUI reachable: `curl -s -o NUL -w "%{http_code}" http://127.0.0.1:8188/system_stats` = 200.
3. `ffmpeg` on PATH (`ffmpeg -version`).
4. Wan models present in `C:\Users\danie\ComfyUI\ComfyUI\models\`
   (`wan2.2_i2v_{high,low}_noise_14B_fp8_scaled`, `wan22_lightning_i2v_4steps_{high,low}`,
   `umt5_xxl_fp8_e4m3fn_scaled`, `wan_2.1_vae`). Missing → `FAILED: Wan models missing`.
5. Skill scripts present next to this file: `wan_render.py`, `overlay.py`.

Work dir: `C:\Users\danie\reel-work\note-<yyyymmdd-hhmmss>\` — create it.

## Step 1 — Fetch the source image

Download `image_url` into the work dir as `source.png`:

```
curl -sL -o "C:\Users\danie\reel-work\note-<ts>\source.png" "<image_url>"
```

Verify the file exists and is non-empty → else `FAILED: image download failed`.

## Step 2 — Split the quote into ≤2 lines

Split `text` into one or two lines for the overlay:
- Max ~8 words per line — longer overflows the 832px frame.
- No single word > 11 characters in line 2 — the ASS wrap is primitive.
- If `text` is short, line 2 may be empty (`""`).
Balance the two lines so they read naturally.

## Step 3 — Wan i2v render

Run from this skill's directory:

```
python wan_render.py "C:\Users\danie\reel-work\note-<ts>\source.png" "C:\Users\danie\reel-work\note-<ts>" note
```

Wan 2.2 i2v Lightning, 4 steps, 832x480, 97 frames @ 24fps (~4s). ~3-6 min on
the RTX 3060. The script uploads the image to the local ComfyUI, queues,
polls, and writes the result MP4 into the work dir. Capture its path (printed
as `downloaded: <path>`).

Optionally pass a 4th arg — a content-aware motion prompt (10-30 words
describing what subtly moves in this specific image) — for a better result
than the generic default.

**Wait for the render SYNCHRONOUSLY in the foreground** — run `wan_render.py`
as a blocking foreground command (it polls ComfyUI internally) and do not
return until it prints `downloaded: <path>`. NEVER launch it as a background
task and NEVER end your turn to "wait for a background task notification":
this is a headless `claude -p` run — the moment the turn ends the process
exits, the worker finds no `RESULT_URL:` and flips the job to failed while
ComfyUI is still rendering (incident 2026-07-12, job 80e09dda).

## Step 4 — Quote overlay

Run from this skill's directory:

```
python overlay.py "<raw-wan-mp4>" "C:\Users\danie\reel-work\note-<ts>\final.mp4" "<line 1>" "<line 2>" [accent_word]
```

Pass `accent_word` only if it is not `(none)` and actually appears in line 2.
Output is the muted final MP4.

## Step 5 — Upload to R2

Upload `final.mp4` to R2 and get a public URL. Run an inline script from
`C:\Users\danie\article-forge` via `node --env-file=.env.local`, using the
R2 client in `lib/r2.ts` (read that file to pick the right helper / S3
client; R2 creds come from `.env.local`). Store it under a `video-notes/`
key prefix. Capture the returned public URL.

## Step 6 — Report

Print the final R2 URL as the last line:

```
RESULT_URL: <r2-mp4-url>
```

The worker captures it, writes `video_jobs.video_url`, flips the job to
`done`, and fires the ntfy notification. Print nothing after it.

## Anti-patterns

- Never ask Daniel anything. Never pause.
- Never publish to Substack — that stays a manual drag-and-drop step.
- Never end the run without printing `RESULT_URL:` or `FAILED:`.
- Never wait for anything via background tasks / "task notifications" —
  headless `-p` run ends (and the job fails) the moment you end your turn.
  All waiting = blocking foreground poll loops.
