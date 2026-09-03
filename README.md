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
ai-media-generation see-through
```

## See-through

キャラクター部位への分解は [See-through](https://github.com/shitagaki-lab/see-through) 本家 CLI を使う。ComfyUI のカスタムノードは不要。

1. 本家をクローンし、公式手順で Python 3.12 環境を用意する
2. `.env` に `SEE_THROUGH_ROOT`（クローン先）と `SEE_THROUGH_PYTHON`（その環境の Python）を書く
3. 画像を渡す

```bash
ai-media-generation see-through path/to/image.png
```

部位 PNG は `see-through-output/<stem>/layers/` に保存される。初回は本家が Hugging Face から重みを取得する。
