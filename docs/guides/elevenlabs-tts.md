---
title: "Configure ElevenLabs TTS for a Hermes Profile"
slug: "elevenlabs-tts"
category: "guides"
tags: ["tts", "elevenlabs", "voice", "configuration", "telegram", "security"]
sources:
  - "sessions/2026-05-27-hermes-pull-105-commits-codex-fix-tts-cornelia.md"
last_updated: "2026-05-28"
version: 1
hermes_version_min: "0.14.0"
---

# Configure ElevenLabs TTS for a Hermes Profile

This guide shows a least-privilege way to enable ElevenLabs text-to-speech for one Hermes profile while keeping the API key scoped and out of the repository.

## 1. Create a scoped ElevenLabs key

In the ElevenLabs dashboard, create an API key with the smallest useful permission set for Hermes TTS:

- **Usage limit**: set a hard monthly cap appropriate to the profile.
- **Allow**:
  - Text to Speech: access
  - Voices: read
  - Models: access
  - User: read
  - History: read, optional
- **Deny** unless separately needed:
  - Speech to Speech
  - Sound Effects
  - Music Generation
  - Dubbing
  - Voice Generation
  - Workspace administration
  - Service accounts
  - Webhooks
  - Audit log

The point is blast-radius control. A TTS key should not be able to administer the ElevenLabs workspace.

## 2. Store the key outside the repo

Secrets belong in environment files or a secret manager, not in docs or Git.

Example using a profile-local `.env` file:

```bash
PROFILE=family-staging
ENV_FILE=~/.hermes/profiles/$PROFILE/.env

{
  grep -v '^ELEVENLABS_API_KEY=' "$ENV_FILE" 2>/dev/null || true
  printf 'ELEVENLABS_API_KEY=%s\n' "$ELEVENLABS_API_KEY"
} > /tmp/hermes-profile.env
mv /tmp/hermes-profile.env "$ENV_FILE"
chmod 600 "$ENV_FILE"
```

If you use 1Password, read the value directly from `op` and still write only to the profile `.env`. Always pass `--vault <name>` when using a service account.

## 3. Discover Italian shared voices

ElevenLabs shared voices can be queried by language:

```bash
KEY=$(grep '^ELEVENLABS_API_KEY=' ~/.hermes/profiles/<profile>/.env | cut -d= -f2-)

curl -s \
  -H "xi-api-key: $KEY" \
  'https://api.elevenlabs.io/v1/shared-voices?language=it&page_size=15'
```

Observed Italian candidates from the source session:

| Voice | Voice ID | Notes |
|---|---|---|
| Cornelia | `SKEVNjRKCergbPKum64u` | Warm, calm, standard accent; high community social proof |
| Aurora | `3LTv5xMEHTJYUIMl1jBR` | Calm authority, Milanese accent |
| Daniela Narrator | `VZOd9FMXDnXRZpGn0thg` | Professional narrator style |

Shared voices that allow direct TTS can be used by `voice_id` without first adding them to the personal voice library.

## 4. Test direct generation

```bash
curl -X POST 'https://api.elevenlabs.io/v1/text-to-speech/SKEVNjRKCergbPKum64u' \
  -H "xi-api-key: $KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Ciao, sono Kai. Questo è un test della nuova voce italiana.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.55,
      "similarity_boost": 0.75,
      "use_speaker_boost": true
    }
  }' \
  --output /tmp/elevenlabs-test.mp3
```

The source session validated MP3 output with `eleven_multilingual_v2` and Cornelia.

## 5. Configure the Hermes profile

Patch the profile config after human approval of the voice sample:

```yaml
tts:
  provider: elevenlabs
  elevenlabs:
    voice_id: SKEVNjRKCergbPKum64u
    model_id: eleven_multilingual_v2
```

Restart the gateway for that profile:

```bash
systemctl --user restart hermes-gateway-family-staging.service
```

## 6. Telegram delivery formats for samples

Hermes text sending is not a general audio delivery pipeline. For voice samples, use the Telegram Bot API directly:

- `sendVoice` with Opus `.ogg` for voice-note UX.
- `sendAudio` with `.mp3` for a playable, saveable, forwardable audio file.

Convert MP3 to Opus voice note:

```bash
ffmpeg -i /tmp/elevenlabs-test.mp3 -c:a libopus -b:a 32k /tmp/elevenlabs-test.ogg
```

## Cost guardrail

The source session estimated short briefings at roughly 150-300 ElevenLabs credits each. A hard cap protects against runaway TTS loops and should be treated as mandatory for always-on assistant profiles.
