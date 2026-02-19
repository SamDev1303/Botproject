# Media Vault Policy

Root workspace must stay free of generated media files.

## Canonical folder

- `media-vault/images`
- `media-vault/videos`
- `media-vault/audio`
- `media-vault/documents`
- `media-vault/exports`

## Rule

- Do not save new `.png`, `.jpg`, `.mp4`, `.mp3`, `.pdf` files to workspace root.
- Move or create all new media directly under `media-vault/*`.

## Utility

```bash
bash scripts/store-media-asset.sh <file_path> [category]
```

Examples:

```bash
bash scripts/store-media-asset.sh ./preview.png
bash scripts/store-media-asset.sh ./recording.mp4 videos
```
