---
name: restack-video-note-auto
description: >
  Autonomous, GATELESS variant of restack-video-note. Runs unattended on
  Daniel's home PC (RTX 3060), invoked by the video-worker via `claude -p`
  for `kind: restack-video-note` queue jobs. Generates a talking-head video
  of Daniel's avatar speaking the supplied commentary (karaoke captions +
  DIGITAL CRAFT WORKSHOP header burned in), uploads the final MP4 to R2.
  Pipeline: Codex image_gen (avatar in environment, character reference) →
  ElevenLabs TTS in cloned voice → InfiniteTalk lip-sync (Wan 2.1 I2V 14B +
  InfiniteTalk Single + Lightx2v rank64 LoRA, 640×640, full block swap) →
  karaoke ASS captions + DCW header → R2 upload. No approval gates. Do NOT
  use interactively — for hands-on use `restack-video-note`.
---

# restack-video-note-auto

Gateless autonomous talking-head pipeline. Sister to `restack-video-note`
but with every approval gate removed and the input taken from a queue
payload instead of being interactive. Run by `video-worker` against a
`video_jobs` row of `kind: restack-video-note`.

## Invocation contract

The worker invokes this skill with three inputs in the prompt:

- `text` — the commentary the avatar will speak (10-35 words, plain EN)
- `env` — optional environment phrase (e.g. `behind a wooden desk with a
  laptop and a coffee mug`); if `(none)`, pick one at random from the list
  in step 1
- `note_id` — optional grownote note id for filenames; if `(none)`, use a
  timestamp

On success: print exactly `RESULT_URL: <r2-mp4-url>` as the last line.
On failure: print exactly `FAILED: <one-line reason>` as the last line.
The worker greps for these. Never end without one of them.

## Operating rules (gateless)

- **Never ask Daniel anything. Never pause.** No human is in the loop.
- **Never publish to Substack** — that stays a manual drag-and-drop step.
- **Fail loud, fail fast.** On any unrecoverable error print `FAILED: <reason>` and stop.
- All paths below are Windows paths on the home PC.

## Pre-flight (abort with FAILED if any check fails)

1. Article Forge repo at `C:\Users\danie\article-forge` with `.env.local`
   (needs `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `R2_*`).
2. ComfyUI reachable locally:
   `curl -s -o NUL -w "%{http_code}" http://127.0.0.1:8188/system_stats` = 200.
3. `ComfyUI-WanVideoWrapper` custom node + InfiniteTalk models in
   `ComfyUI\models\diffusion_models\InfiniteTalk\` and
   `ComfyUI\models\diffusion_models\Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors`.
   Missing → `FAILED: InfiniteTalk models missing`.
4. Codex logged in: `codex login status` must say "Logged in using ChatGPT".
5. Avatar reference at `C:\Users\danie\restack-assets\avatar-reference.png`.
6. `ffmpeg` on PATH.

Work dir: `C:\Users\danie\restack-work\auto-<note_id or yyyymmdd-hhmmss>\` — create it.

## Step 1 — Environment

If `env` is `(none)`, pick ONE at random:
- `sitting behind a wooden desk with a laptop and a coffee mug`
- `sitting at a PC desk with dual monitors`
- `at a workbench with tools and parts`
- `at a standing desk with a mechanical keyboard`
- `beside a whiteboard with diagrams`
- `in a home office at night with warm lamp light`

## Step 2 — Codex image_gen (avatar in scene)

Write the prompt to a file then pipe into `codex exec` via stdin (positional
arg is dropped when crossing SSH+PowerShell):

```
@'
Square 1:1 image. The character with short beard, blue eyes, dark navy snapback with a red 4-pointed star, red jacket over dark hoodie, <env>, looking at the camera with a friendly natural expression, head and shoulders clearly visible and well lit. Brand palette deep navy background, subtle teal and orange accents. Flat bold vector illustration style. Use your built-in image_gen tool with the attached image as the character reference. Save the final image as scene.png in the current working directory. No text, no logos, no other realistic faces.
'@ | Set-Content -Encoding utf8 <workdir>\prompt.txt

Get-Content <workdir>\prompt.txt -Raw | codex exec --dangerously-bypass-approvals-and-sandbox -C "<workdir>" -i "C:\Users\danie\restack-assets\avatar-reference.png" *> <workdir>\codex.log
```

Verify `<workdir>\scene.png` exists and is non-empty → else retry once → else `FAILED: codex image gen failed`.

## Step 3 — Center-crop + resize 640×640

InfiniteTalk runs at 640², KJNodes not installed — resize on the PC:

```
& C:\Users\danie\ComfyUI\python_embeded\python.exe -c "from PIL import Image; im=Image.open(r'<workdir>\scene.png').convert('RGB'); w,h=im.size; s=min(w,h); im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((640,640),Image.LANCZOS).save(r'C:\Users\danie\ComfyUI\ComfyUI\input\restack-auto-<id>-scene.png')"
```

## Step 4 — TTS

`tts.py` reads ElevenLabs creds from the env file pointed to by `AF_ENV`
and writes the wav + words JSON to `TTS_OUT_DIR`:

```
$env:AF_ENV = "C:\Users\danie\article-forge\.env.local"
$env:TTS_OUT_DIR = "<workdir>"
& C:\Users\danie\ComfyUI\python_embeded\python.exe (Join-Path (Split-Path $PSScriptRoot) "restack-video-note-auto\tts.py") "<text>" voice
```
(or use the absolute path to `tts.py` in this skill dir.)

Output: `<workdir>\voice.wav` + `<workdir>\voice.words.json`. Capture the
duration printed on the last line.

Copy the wav to ComfyUI input:
```
Copy-Item <workdir>\voice.wav C:\Users\danie\ComfyUI\ComfyUI\input\restack-auto-<id>-voice.wav -Force
```

## Step 5 — Convert workflow + queue InfiniteTalk render

```
$env:COMFY_HOST = "http://127.0.0.1:8188"
& C:\Users\danie\ComfyUI\python_embeded\python.exe <skill_dir>\convert_workflow.py restack-auto-<id>-scene.png restack-auto-<id>-voice.wav restack-auto-<id> <workdir>\api.json
& C:\Users\danie\ComfyUI\python_embeded\python.exe <skill_dir>\queue_it.py <workdir>\api.json
```

`queue_it.py` writes the result MP4 to `RENDER_OUT_DIR` (set this to
`<workdir>` first via `$env:RENDER_OUT_DIR`). Render ~15-25 min on the
RTX 3060 (fp8 base + full block swap + Lightx2v 6-step LoRA).

**Wait for the render SYNCHRONOUSLY in the foreground** — run `queue_it.py`
as a blocking foreground command (it polls ComfyUI internally; set a generous
Bash timeout, ≥30 min) and do not return until the MP4 lands in
`RENDER_OUT_DIR`. NEVER launch the wait as a background task and NEVER end
your turn to "wait for a background task notification": this is a headless
`claude -p` run — the moment the turn ends the process exits, the worker
finds no `RESULT_URL:` and flips the job to failed while ComfyUI is still
rendering (incident 2026-07-12, job 80e09dda). If the foreground command hits
a tool timeout mid-render, resume with a blocking foreground poll loop
(`time.sleep(15)` + GET `/history/<prompt_id>`), never a background task.

## Step 6 — Captions + DCW header

```
$env:FFMPEG = "ffmpeg"
$env:FFPROBE = "ffprobe"
& C:\Users\danie\ComfyUI\python_embeded\python.exe <skill_dir>\captions.py <workdir>\restack-auto-<id>_00001-audio.mp4 <workdir>\final.mp4 <workdir>\voice.words.json
```

Karaoke ASS (red `\kf` sweep through white words) + DIGITAL CRAFT WORKSHOP
header (top-left, white + red WORKSHOP + thin red underline), all hard-pinned
to the same bottom anchor.

## Step 7 — Upload final MP4 to R2

Upload `<workdir>\final.mp4` to R2 under the `restack-videos/` prefix using
the article-forge R2 client. From `C:\Users\danie\article-forge`:

```
node --env-file=.env.local -e "
const fs=require('fs');
const {S3Client,PutObjectCommand}=require('@aws-sdk/client-s3');
const c=new S3Client({region:'auto',endpoint:process.env.R2_ENDPOINT,credentials:{accessKeyId:process.env.R2_ACCESS_KEY_ID,secretAccessKey:process.env.R2_SECRET_ACCESS_KEY}});
const key='restack-videos/<id>-<ts>.mp4';
(async()=>{await c.send(new PutObjectCommand({Bucket:process.env.R2_BUCKET,Key:key,Body:fs.readFileSync(process.argv[1]),ContentType:'video/mp4'}));console.log(process.env.R2_PUBLIC_BASE+'/'+key)})()
" <workdir>\final.mp4
```

If the article-forge repo has `lib/r2.ts` (or similar), prefer that helper
via `npx tsx -e "..."`. Capture the printed public URL.

## Step 8 — Report

Print the final R2 URL as the LAST line:
```
RESULT_URL: <r2-mp4-url>
```

The worker captures it, writes `video_jobs.video_url`, flips the job to
`done`, and fires the Telegram notification.

## Anti-patterns

- Never ask Daniel anything. Never pause.
- Never publish to Substack — manual drag-and-drop in Note compose.
- Never end the run without printing `RESULT_URL:` or `FAILED:`.
- Never run multiple InfiniteTalk renders in parallel — the 12GB VRAM only
  fits one. The worker already serialises by claiming one job at a time.
- Never wait for anything via background tasks / "task notifications" —
  headless `-p` run ends (and the job fails) the moment you end your turn.
  All waiting = blocking foreground poll loops.
