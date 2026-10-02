# 手寫筆記對照閱讀網站

靜態網站：左邊是（對比增強後的）手寫頁面圖片，右邊是 OCR 後的排版文字。支援多份 PDF，部署於 GitHub Pages。

## 資料夾結構

```
pdfs/<slug>.pdf                 原始 PDF（不進 git）
docs/<slug>/meta.json           標題、副標、PDF 路徑、排序
docs/<slug>/ocr/page_NNN.md     每頁 OCR 結果（進 git，可人工修改）
tools/enhance.py                對比增強函式
tools/render.py <slug> [--force]  PDF -> 網站頁面圖 + 封面 + OCR 用圖
tools/new_doc.py                新增一份 PDF
tools/build.py                  OCR md -> site/docs/<slug>/data.js + site/library.js
site/                           GitHub Pages 發佈內容（全部進 git）
work/<slug>/ocr_img/            OCR 用圖（不進 git）
.github/workflows/pages.yml     push 到 main 時部署 site/
```

slug 只能用小寫英數字與連字號（`^[a-z0-9-]+$`），因為會出現在網址。

## 新增一份 PDF

1. 建立文件並產生圖片：
   ```
   .venv/bin/python tools/new_doc.py /path/to/file.pdf my-slug --title "標題" --subtitle "副標"
   ```
   這會複製 PDF 到 `pdfs/`、寫入 `docs/my-slug/meta.json`、建立空的 `ocr/`，並渲染 `site/docs/my-slug/pages/`、`cover.jpg` 與 `work/my-slug/ocr_img/`。
2. OCR：由 Claude 子代理逐頁讀取 `work/my-slug/ocr_img/page_NNN.png`，依 `PLAN.md` 的「OCR 規則」寫入 `docs/my-slug/ocr/page_NNN.md`。每個子代理處理 10 頁，完成後再做一輪放大分段（zoomed-strip）的校對。
3. 建置：`.venv/bin/python tools/build.py`
4. 提交並推送：`git add -A && git commit -m "add my-slug" && git push`

## 修正 OCR 文字

編輯 `docs/<slug>/ocr/page_NNN.md` → 執行 `.venv/bin/python tools/build.py` → commit 並 push。

## 本機預覽

```
.venv/bin/python -m http.server -d site 8000
```

開啟 http://localhost:8000 。也可直接用 file:// 開啟 `site/index.html`。

重新渲染圖片（例如調整增強參數後）：`.venv/bin/python tools/render.py <slug> --force`。

## 公開 / 不公開

- `docs/<slug>/meta.json` 的 `"publish"` 決定是否部署到 GitHub Pages。`new_doc.py` 新增的文件預設 `false`（加 `--publish` 才會公開）。
- `tools/build.py` 會：
  - `site/library.js`：只列 `publish: true` 的文件（部署用）。
  - `site/library.preview.js`：列全部文件，只在本機預覽時出現（已被 git 忽略）。
  - 自動在 `.gitignore` 產生一段清單，把未公開文件的 `docs/<slug>/` 與 `site/docs/<slug>/` 排除在 git 之外，所以不會被 commit 或 push。
- 要公開某份：把 `"publish"` 改成 `true` → `tools/build.py` → commit、push。
