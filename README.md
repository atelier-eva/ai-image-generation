# ai-media-generation

## インストール

```bash
uv tool install git+https://github.com/atelier-eva/ai-media-generation.git
```

## 使い方

```bash
ai-media-generation init
ai-media-generation lora-training
ai-media-generation image
ai-media-generation music
ai-media-generation report
```

`image` の `COMFY_UI_FILENAME_PREFIX` はファイル名用（サブフォルダではない）。以前の `image-output/<prefix>/...` 配下の成果物はそのまま残る。
