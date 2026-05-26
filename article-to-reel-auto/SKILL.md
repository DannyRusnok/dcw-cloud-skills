---
name: article-to-reel-auto
description: >
  Autonomous, GATELESS variant of article-to-reel / article-to-tldr. Runs
  unattended on Daniel's home PC (RTX 3060), invoked by the reel-jobs worker
  via `claude -p`. Generates a 9:16 reel or TLDR video end-to-end with NO
  human approval steps: scenario → per-scene images via Codex CLI built-in
  image_gen → ElevenLabs TTS → Wan 2.2 i2v render → compose → R2 upload.
  Daniel reviews the finished MP4 afterwards, not mid-flight. Do NOT use this
  skill interactively — for hands-on reels with approval gates use the
  original `article-to-reel` / `article-to-tldr` skills instead.
---

# article-to-reel-auto

Gateless autonomous reel/TLDR pipeline. Sister to `article-to-reel` and
`article-to-tldr` but with **every approval gate removed** and the manual
ChatGPT image step **replaced by Codex CLI image generation**. Designed to be
run by the `video-worker` on the home PC against a `video_jobs` queue row.

## Invocation contract

The worker invokes this skill with four inputs in the prompt:

- `article_id` — UUID of the article in `articleforge.articles`
- `format` — `reel` (standalone 30-45s social cut, has CTA) or `tldr`
  (25-40s inline recap, NO CTA)
- `note` — optional free-text steer (may be empty)
- `rerender_scene` — a scene number for incremental mode, or `(none)` for a
  full render (see "Incremental mode" below)

On success: print exactly `RESULT_URL: <r2-mp4-url>` as the last line.
On failure: print exactly `FAILED: <one-line reason>` as the last line.
The worker greps for these. Never end without one of them.

## Operating rules (gateless)

- **Never ask a question. Never wait for approval.** There is no human in
  the loop. If a decision is needed, make the reasonable choice and proceed.
- **Never stop to confirm cost.** Spending ElevenLabs credits + GPU time is
  expected — that is the whole point of this skill.
- **Fail loud, fail fast.** On any unrecoverable error, stop and print
  `FAILED: <reason>`. Do not silently degrade to a Ken Burns draft — per
  Daniel's policy the final output is always video-from-image.
- All paths below are Windows paths on the home PC.

## Pre-flight (abort with FAILED if any check fails)

1. Article Forge repo present at `C:\Users\danie\article-forge` with
   `.env.local` (needs `DATABASE_URL`, `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`,
   `ELEVENLABS_VOICE_ID`, `R2_*`). All script commands run from there.
2. Avatar reference image at `C:\Users\danie\reel-assets\avatar-reference.png`.
   If missing → `FAILED: avatar reference image not found`.
3. Codex logged in: `codex login status` must say "Logged in using ChatGPT".
4. ComfyUI reachable on the PC: `curl -s -o NUL -w "%{http_code}" http://127.0.0.1:8188/system_stats` = 200.
   ComfyUI runs locally on the PC so no SSH tunnel is needed here.
5. Wan models present in `C:\Users\danie\ComfyUI\ComfyUI\models\`
   (`diffusion_models\wan2.2_i2v_{high,low}_noise_14B_fp8_scaled.safetensors`,
   `loras\wan22_lightning_i2v_4steps_{high,low}.safetensors`,
   `text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors`,
   `vae\wan_2.1_vae.safetensors`). Empty → `FAILED: Wan models missing`.
6. `ffmpeg` on PATH (`ffmpeg -version`). Missing → `FAILED: ffmpeg not found`.

Ensure the per-job work dir `C:\Users\danie\reel-work\<article_id>\` exists
(create if absent). **Never wipe it** — its cached scene images and
`wan-*.mp4` clips are what make incremental re-renders cheap.

## Incremental mode — when `rerender_scene` is a number

If `rerender_scene` is a scene number (not `(none)`), do NOT run the full
pipeline below. Re-render only that one scene and recompose, reusing every
cached artifact already in the work dir.

Abort with `FAILED: incremental needs a prior full render` if the work dir is
missing `scenario.json`, `scene_audio.json`, or the other scenes' `wan-*.mp4`.

1. Read `scenario.json` + `scene_audio.json` from the work dir; locate the
   target scene (`id` == `rerender_scene`). Query the DB for the latest
   `article_videos` row for this article **WHERE format matches the job's
   `format` input** (`reel` or `tldr`) — that is the `video_id` for Step 7.
   Picking the latest row of any format silently re-renders the wrong asset
   (e.g. a TLDR job overwrites the reel's last render).
2. Regenerate ONLY that scene's image with Codex — Step 3 mechanics, applying
   the `note` steer + pose rules. Overwrite `scene-<N>.png`.
3. Upload it to R2 — Step 4 — and patch only that scene's `imageUrl` in
   `scenario.json`.
4. Re-render ONLY that scene's Wan clip — Step 6 mechanics — overwriting
   `wan-<N>.mp4`. Narration is unchanged; reuse the scene's existing audio
   timing for frame length.
5. Recompose with `build-wan-reel.ts` — Step 7 — passing ALL `wan-*.mp4` in
   scene order (the fresh `wan-<N>.mp4` plus every untouched clip). This also
   re-applies the current chrome/content overlays to every scene.
6. Visual self-check (Step 8), upload final (Step 9), report (Step 10).

Do NOT regenerate the scenario, do NOT re-run TTS, do NOT touch other scenes.
This path is ~10 minutes instead of ~80. For a full render (`rerender_scene`
= `(none)`) run every step below in order.

## Note mode — when `format: note`

Single-scene muted promo video for Substack feed autoplay. Defaults muted because Substack feed plays without sound; the goal is a thumb-stopping 4-6s loop, not a narrated explainer. Use this format when the worker prompt has `format: note`.

Pipeline differs from `reel`/`tldr`:

1. Load article (Step 1 below). Extract:
   - `cover_image_url` (REQUIRED — the visual base for the Wan i2v render). If null, abort with `FAILED: article missing cover_image_url — generate cover first via cover-image-generate skill`.
   - `hook_text` (from worker prompt) OR auto-pick: prefer `subtitle` if 5-12 words; else first sentence of `content` trimmed to 12 words; strip trailing period.
   - `accent_word` (from worker prompt) OR auto-pick: the first numeric token (`$2`, `5x`, `120k`) OR the first proper noun in the hook.

2. Download `cover_image_url` to work dir as `note-source.png`. Do NOT call Codex — reuse the cover that's already brand-compliant.

3. Submit ONE Wan 2.2 i2v render: image=note-source.png, length=97 frames @ 16fps = 6.0625s, prompt="Subtle camera drift, gentle parallax, soft light shift, no scene change, no character change", negative="static, frozen, abrupt motion, scene cut". This is intentionally low-motion to avoid distracting from the text overlay. Save as `note-bg.mp4`.

4. Skip TTS entirely. Skip `scene_audio.json`. There is no spoken audio.

5. Generate ASS overlay file `note-overlay.ass`:
   - Style: white text `#e2e8f0` on subtle dark gradient strip (bottom third), `Inter` or fallback `Arial Black`, font size 64-80 depending on hook length.
   - Position: `\an2\pos(540,1500)` (bottom center, leaves room for Substack UI chrome).
   - Single dialogue line spanning 0:00.00 to end of clip (6s).
   - If `accent_word` is present in hook, wrap that token in `{\c&H0026DC&}<word>{\c&HE2E8F0&}` so it pops red (BGR &H0026DC = #DC2600 orange-red, matches DCW accent). Match case-insensitively but preserve original casing.

6. Compose via ffmpeg:
   ```
   ffmpeg -i note-bg.mp4 -vf "ass=note-overlay.ass" -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -movflags +faststart -an note-final.mp4
   ```
   Note `-an` = no audio track. `-movflags +faststart` = mobile-friendly streaming.

7. Visual self-check (Step 8 mechanics): read frame at 3s; verify text legibility, accent word color, no clipping.

8. Upload via `uploadArticleVideo` (R2 cover-context bucket OR video bucket — match other formats). INSERT a new `article_videos` row with `format='note'`, `video_url=<r2-url>`, `duration_seconds=6.0`, scenario_json={hook_text, accent_word, source: cover_image_url}.

9. Report `RESULT_URL: <url>`.

Time budget: ~6-8 min total (1 Wan render + ffmpeg compose). No Codex spend, no ElevenLabs spend.

Constraints:
- ONE scene only. Multi-scene notes get truncated by Substack autoplay anyway.
- ALWAYS muted. Even if Daniel later wants audio, the audio track stays off — the format is defined as muted feed bait.
- ALWAYS overlay text. No silent video without a hook — it's promo, not art.

## Audio-recompose mode — when `mode: audio-recompose`

If the worker prompt contains `mode: audio-recompose`, do NOT run any of the
full pipeline OR the incremental rerender_scene path. This mode refreshes ONLY
the spoken audio + final composition. Wan video backgrounds and Codex scene
images stay frozen.

Use case: Daniel hand-edited `scenario_json.scenes[].narration` in the DB and
wants the audio to match the new text without re-rendering ~25 GB of Wan video.

Abort with `FAILED: audio-recompose needs prior full render` if the work dir
is missing any of `scene-N.png`, `wan-N.mp4`, or has no scenario at all.

1. Query the DB for the latest `article_videos` row WHERE `article_id` matches
   AND `format` matches the job's `format` (`reel` or `tldr`). This is the
   source scenario AND the row whose work dir we're going to reuse.
2. Pull `scenario_json` from that row and write it to `scenario.json` in the
   work dir, overwriting any older copy. The DB is the source of truth here —
   Daniel may have edited narrations there.
3. For each scene in order, re-run ElevenLabs TTS (Step 5b mechanics). The
   ElevenLabs lib caches per-narration-text on disk — scenes whose narration
   didn't change return their cached `mp3` in milliseconds. Only changed
   scenes hit the API. Update `scene_audio.json` with fresh word timestamps.
4. Verify EVERY `wan-N.mp4` exists in the work dir; if any is missing, abort
   with `FAILED: missing cached background for scene N — run full render first`.
5. Regenerate the ASS karaoke captions from the fresh `scene_audio.json`
   (Step 7's caption sub-step) — word timing changes per take even with the
   same narration text, so captions ALWAYS regenerate.
6. Insert a NEW `article_videos` row tagged with the correct `format` (do NOT
   overwrite the source row — keep history). Use `render-byo-reel.ts` with the
   `--format` flag matching the job, OR an inline psql INSERT that copies the
   scenario from step 2.
7. Recompose via `build-wan-reel.ts` (Step 7), passing every existing
   `wan-N.mp4` in scene order. The script re-applies chrome/content overlays
   and karaoke captions using the new audio.
8. Visual self-check (Step 8) — at minimum spot-check the scene whose
   narration changed for audio-caption sync drift. Upload final (Step 9),
   report `RESULT_URL: <url>` (Step 10).

Constraints:
- Do NOT regenerate the scenario via Haiku.
- Do NOT touch Codex (scene images stay byte-identical).
- Do NOT touch Wan (background videos stay byte-identical).
- If any new narration is MUCH longer than the original (more than ~10% over
  the existing `wan-N.mp4`'s frame budget), ABORT with
  `FAILED: scene N narration exceeds cached background length — re-run with
  rerender_scene=N to refresh the bg, or trim the narration`. Better to refuse
  than to ship audio/video drift.

This path is ~2–3 minutes (TTS for changed scenes + ffmpeg compose + upload).
Per-render cost: zero Codex, zero Wan, only the ElevenLabs character delta.

## Step 1 — Load the article

Read the article straight from the DB (no MCP needed locally):

```
node --env-file=.env.local -e "const p=require('postgres');const s=p(process.env.DATABASE_URL);s\`select id,title,subtitle,content,published_url,platform from articleforge.articles where id=${'<article_id>'}\`.then(r=>{console.log(JSON.stringify(r[0]));return s.end()})"
```

Empty result → `FAILED: article not found`.

## Step 2 — Generate the scenario

Write the scene plan yourself (you are Claude — this is the Haiku step done
inline). Apply the `note` steer if present.

**Scene count + arc:**

- `format: reel` — 4-5 scenes, 70-100 words narration total, 30-45s.
  Arc: HOOK → mechanism → mechanism → receipts → CTA (one-line "read more").
- `format: tldr` — 3-4 scenes, 60-90 words, 25-35s.
  Arc: HOOK → problem → solution → receipts. **NO CTA scene, no "link in
  bio", no "subscribe", no "follow".** Last scene = last beat of the article.

**Per scene fields** (this is the `VideoScenario` shape the render scripts
expect — see `lib/db/schema.ts`):
`id`, `narration` (1-2 full sentences, no telegraphic fragments),
`headline` (2-5 words, ≤14 chars to avoid chrome overflow — internal label,
also rendered as small subtitle under the big visual),
`visualKind` (`title` for tldr always; `title`/`stat`/`bullet`/`quote`/`cta`
for reel),
`visualText` — the BIG on-screen text. MUST be semantically distinct from
`headline` (never the same string, never just an all-caps version). Format
per kind:
- `stat` — JUST the number or ≤8-char phrase (e.g. `$2`, `250 lines`). Never
  a topic label like `DEAD MEMORY`.
- `title` — short on-screen sentence (≤11 chars/line, ≤4 lines). The IDEA,
  not a label.
- `quote` — one pulled sentence (≤100 chars).
- `bullet` — REQUIRED FORMAT: exactly 3 short items separated by ` | `,
  each ≤22 chars. Example: `SessionStart | UserPromptSubmit | SessionEnd`.
  If the beat can't be expressed as 3 items, switch `visualKind` to `title`.
- `cta` — short call to action (e.g. `Read the full post`).
Good pair example: `headline: "Three lifecycle hooks"`,
`visualText: "SessionStart | UserPromptSubmit | SessionEnd"`.
ANTI-EXAMPLE (banned — the renderer drops/demotes it): both fields set to
`"THREE HOOKS"`.
Then `accent` (`teal`/`orange`/`navy`), `imageUrl` (filled in Step 4),
optional `titleOffsetY`.

Narration language = **English** (publishing-output rule). Keep sentences
plain and short — readable for non-native viewers.

Hold the scenario JSON in memory; you patch `imageUrl` per scene after Step 4.

## Step 3 — Generate per-scene images with Codex

For EACH scene, generate one 9:16 image via Codex's built-in `image_gen`
tool. This replaces the manual ChatGPT step.

3a. Use this EXACT prompt template. Only substitute `<SCENE-SPECIFIC ACTION>`
    — the rest is verbatim and must appear in the order shown. The leading
    style sentence and the closing strict block are load-bearing; rewording
    them lets Codex drift into photorealism.

```
Flat bold vector illustration in the EXACT style of the attached reference image. Cel-shaded, clean bold outlines, flat solid color fills, comic-book line work, no photorealism. 9:16 vertical portrait composition.

Scene: <SCENE-SPECIFIC ACTION>. Calm focused expression, mouth closed, not speaking. The character is the same person as in the reference image: short beard, blue eyes, dark navy snapback with a red 4-pointed star, red jacket over a dark hoodie.

Background: deep navy #0f172a with subtle teal #14b8a6 and orange #f59e0b accent lighting. Match the reference image's flat brand style — same line weight, same flat color treatment, same cel-shading.

Strict: NO photorealism, NO 3D render, NO anime, NO painterly textures, NO realistic skin pores, NO realistic fabric texture. NO text, NO logos, NO other realistic faces. Reference-image illustration style only.
```

3a-rules. When writing the `<SCENE-SPECIFIC ACTION>`:
- One clear scene-specific action that matches the beat's emotional tone
  (worried at a laptop for an incident hook, at a desk with glowing
  metrics for a receipts scene, etc.).
- **Each scene MUST have a visually distinct environment.** Before writing
  scene N's action, scan the actions you wrote for scenes 1..N-1 and pick
  a setting clearly different from all of them (different room / pose /
  props / framing). Two scenes both showing "avatar at workshop bench" or
  "avatar at laptop desk" is a failure mode — vary the setting even when
  the beats feel similar.
- Never combine arms-crossed with a broad open smile (reads wrong).
- Never write "smiling broadly", "talking", "saying", or "mouth open" —
  voice-over playback means the character must look still and quiet.

3b. Run Codex headless, one call per scene, attaching the avatar reference:

```
codex exec --dangerously-bypass-approvals-and-sandbox -C "C:\Users\danie\reel-work\<article_id>" -i "C:\Users\danie\reel-assets\avatar-reference.png" "<image prompt>. Use your built-in image_gen tool with the attached image as the character reference. Save the final image as scene-<N>.png in the current working directory."
```

Codex saves built-in output under `$CODEX_HOME\generated_images\...` and then
copies it to `scene-<N>.png` when told to. After each call, verify
`scene-<N>.png` exists and is non-empty; if not, retry that one scene once.
After 2 failures → `FAILED: codex image gen failed for scene <N>`.

Do NOT pass `--search`, do NOT set `OPENAI_API_KEY` — the built-in tool is
plan-covered and must stay on the built-in path, not the metered API CLI.

## Step 4 — Upload scene images to R2

For each `scene-<N>.png`, from `C:\Users\danie\article-forge`:

```
npx tsx scripts/upload-png.ts "C:\Users\danie\reel-work\<article_id>\scene-<N>.png"
```

Capture the printed R2 URL and patch it into that scene's `imageUrl`.
Write the completed `VideoScenario` JSON to
`C:\Users\danie\reel-work\<article_id>\scenario.json`.

## Step 5 — Render base video (TTS + frames + compose)

From `C:\Users\danie\article-forge`:

```
npx tsx scripts/render-byo-reel.ts <article_id> "C:\Users\danie\reel-work\<article_id>\scenario.json" --format <reel|tldr>
```

**ALWAYS pass `--format` matching the job's input `format` parameter** — `reel` for standalone social cut (30-45s, has CTA), `tldr` for inline article embed (25-35s, no CTA). Without `--format`, the row defaults to `reel` and TLDR videos get mis-labeled, which breaks the Article Forge UI tab routing and confuses the rerender-scene path (which picks by format).

This inserts a new `article_videos` row with the injected scenario + correct format, runs ElevenLabs TTS, renders chrome/content frames, composes the base video. Capture the printed `video_id` — needed for Steps 6-7. Record it so the worker can link `reel_jobs.article_video_id`.

## Step 6 — Wan 2.2 i2v per-scene render

For each scene, render an animated background from `scene-<N>.png` on the
local ComfyUI. Mechanics are identical to `article-to-reel` Workflow B:

- Read each `scene-<N>.png` (multimodal) before writing its motion prompt —
  describe what actually moves (character, camera, light), match the
  narration's tone. The narration plays as a voice-over — the character must
  NOT appear to be speaking. Motion prompts must explicitly say "mouth
  closed, not talking, no speaking motion". Negative prompt always includes:
  `text, letters, words, writing, watermark, blurry, distorted, deformed hands,
  talking, speaking, lip sync, lip movement, mouth opening, mouth movement,
  mouth animation, opening mouth, moving lips`.
- Frame length per scene = `ceil((words[-1].end + 0.4) * 16)` from the
  scene's `scene_audio_json` (read it from the `article_videos` row by
  `video_id`), rounded to the nearest `4n+1`. Keep scenes ≤141 frames
  (12GB VRAM); reel scenes that exceed it split-render per Workflow B, tldr
  scenes are always single-pass.
- Submit per scene to `http://127.0.0.1:8188` — dual-sampler Wan 2.2 i2v
  14B fp8 (high-noise UNET + lightning-high LoRA pass 0→2, low-noise UNET +
  lightning-low LoRA pass 2→4), CFG 1.0, euler/simple, 480×832, fps 16.
  Build the API workflow from the blueprint at
  `C:\Users\danie\ComfyUI\ComfyUI\blueprints\Image to Video (Wan 2.2).json`.
- Download each result MP4 to `C:\Users\danie\reel-work\<article_id>\wan-<N>.mp4`.

Render scenes sequentially (single GPU). ~3-7 min/scene on the RTX 3060.

## Step 7 — Recompose with Wan backgrounds

From `C:\Users\danie\article-forge`:

```
node --env-file=.env.local ./node_modules/.bin/tsx scripts/build-wan-reel.ts <video_id> "C:\Users\danie\reel-work\<article_id>\final.mp4" "C:\Users\danie\reel-work\<article_id>\wan-1.mp4" "C:\Users\danie\reel-work\<article_id>\wan-2.mp4" ...
```

(All scene MP4s in scene order.) This re-renders chrome/content overlays
over the Wan backgrounds and keeps captions + DCW branding identical.

## Step 8 — Visual self-check (automated, no gate)

Extract a frame from the start of each scene and Read it multimodally:

```
ffmpeg -y -loglevel error -ss <scene_start_s> -i "...\final.mp4" -frames:v 1 "...\check-<N>.jpg"
```

Check headline overflow (>~14-16 chars crops), caption orphan lines,
brand-chrome overlap. If a fix is needed, shorten the offending `headline`
in the `article_videos.scenario_json` (psql UPDATE) and re-run Step 7
(`build-wan-reel.ts` only — no Wan re-render). At most one fix pass; then
proceed regardless.

## Step 9 — Upload final MP4 to R2

`build-wan-reel.ts` writes only a local file. Upload `final.mp4` to R2 and
mark the `article_videos` row done — one-off inline script from
`C:\Users\danie\article-forge`, run via
`node --env-file=.env.local ./node_modules/.bin/tsx`, using `lib/r2.ts`
`uploadArticleVideo` + a Drizzle update of `article_videos`
(`videoUrl`, `status='done'`). Pattern is in `article-to-tldr` Step 8f.

## Step 10 — Report

Print the final R2 URL as the last line:

```
RESULT_URL: <r2-mp4-url>
```

The worker captures this, writes it to `reel_jobs.video_url`, flips the job
to `done`, and fires the ntfy notification. Do not print anything after it.

## Anti-patterns

- Never ask Daniel anything. Never pause. Never print a "should I…" line.
- Never fall back to Ken Burns / still-image output — Wan video-from-image
  is the only acceptable final.
- Never switch Codex to the metered API CLI (`scripts/image_gen.py` /
  `OPENAI_API_KEY`) — stay on the plan-covered built-in `image_gen`.
- Never reuse a stale `article_videos` row — `render-byo-reel.ts` creates a
  fresh one per run.
- Never end the run without printing `RESULT_URL:` or `FAILED:`.
