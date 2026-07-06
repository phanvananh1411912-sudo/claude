# Podcast Dictation Data Import Guide

## Overview

This guide explains how to import podcast dictation sentences parsed from the Daily Chinese Podcast transcripts into the HSK4 NEXUS application.

## What's Included

- `podcast-sentences-for-import.json` - Complete dataset with 5,765 sentences from 114 podcasts
- `parse-podcasts.mjs` - Parser script to regenerate data if needed

## Format

The JSON file has the structure:
```json
[
  {
    "podcast_id": 1,
    "podcast_lesson_id": 1,
    "sentences": [
      {
        "hanzi": "你好。现在，是晚上了。",
        "pinyin": "nǐ hǎo。 xiàn zài， shì wǎn shàng le。",
        "meaning": "",
        "vi": "",
        "focus": "",
        "orderNum": 0
      },
      ...
    ]
  },
  ...
]
```

## How to Import

### Step 1: Prepare Podcast Lessons
First, make sure you have created podcast lessons in the admin panel (Admin > Podcast luyện nghe > Bài nghe).

### Step 2: Import Sentences
1. Go to Admin > Podcast luyện nghe > Chép chính tả (🎧 Chép chính tả tab)
2. Select a podcast lesson from the dropdown
3. Click "Dán JSON" button
4. Paste the sentences array for that podcast from `podcast-sentences-for-import.json`

For example, for Podcast 1:
```json
[
  {
    "hanzi": "你好。现在，是晚上了。你是不是已经躺在床上了？是不是关了灯，准备睡觉了？",
    "pinyin": "nǐ hǎo。 xiàn zài， shì wǎn shàng le。 nǐ shì bú shì yǐ jīng tǎng zài chuáng shàng le？ shì bú shì guān le dēng， zhǔn bèi shuì jiào le？",
    "meaning": "",
    "vi": "",
    "focus": "",
    "orderNum": 0
  },
  ...
]
```

5. Click "↓ Phân tích & thêm" to import all sentences

### Step 3: Verify Import
- The sentences will appear in the list below
- You can edit individual sentences if needed
- Audio is automatically generated using TTS API

## Notes

- Audio files are generated on-demand using Google Cloud TTS (cached automatically)
- No pre-recorded audio files are needed
- Pinyin, meaning, and Vietnamese translations are imported from the podcast transcripts
- Empty `meaning` and `vi` fields can be filled in manually in the admin interface
- `focus` field is for highlighting grammar/vocabulary focus areas (optional)

## Audio Generation

When students play a sentence, the system:
1. Checks if TTS audio is already cached
2. If not, generates audio using Google Cloud TTS API
3. Caches the audio for future plays
4. Falls back to browser speech synthesis if API is unavailable

## Regenerating Data

If you need to re-parse the podcast transcripts:
```bash
cd /path/to/scratchpad
node parse-podcasts.mjs
```

The script will extract all sentences from the markdown files and generate JSON.
