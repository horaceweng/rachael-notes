# 海訓日誌 對照閱讀網站 — 實作計畫

## 目標
靜態網站：左邊顯示手寫 PDF 頁面圖片，右邊顯示該頁 OCR 後排版好的文字。
可上下頁翻頁、可拖動。不做即時辨識/翻譯，只呈現預先處理好的結果。

## 來源
- `113-C11-Autumn-海訓日誌-翁芮怡.pdf`：49 頁，Apple Notes 匯出的掃描圖，無文字層。
- 繁體中文手寫（藍色原子筆），橫書，部分頁面有彩色插畫。第 18、22–24 頁為橫向。

## 目錄結構
```
notes-demo/
  PLAN.md
  113-C11-...pdf
  work/ocr_img/page_NNN.png   # 170 DPI，給 OCR 用（已產生，不部署）
  ocr/page_NNN.md             # 每頁 OCR 結果（Markdown），人工可修
  build.py                    # ocr/*.md -> site/data.js
  site/                       # 要部署的靜態網站（整個資料夾即可上線）
    index.html                # 單檔：HTML + CSS + JS
    data.js                   # window.PAGES = [{n, img, w, h, md}, ...]
    pages/page_NNN.jpg        # 150 DPI 頁面圖（已產生）
```

## 步驟
1. **頁面轉圖**（已完成）— PyMuPDF 轉出 `work/ocr_img/*.png` 與 `site/pages/*.jpg`。
2. **OCR**（Sonnet 子代理，分 5 批平行）— 逐頁讀圖，寫 `ocr/page_NNN.md`。規則見下。
3. **檢視器**（Haiku 子代理）— 寫 `build.py` 與 `site/index.html`。
4. **驗收**（主模型）— 抽查 OCR 品質、在瀏覽器測翻頁/拖動/手機版。
5. **部署** — 見最後一節，由使用者決定。

## OCR 規則（`ocr/page_NNN.md`）
- 逐字照抄，保留原文用字（含錯字、口語、表情符號式寫法），**不潤飾、不改寫、不翻譯**。
- 依原稿分段；原稿的換行若只是因為紙張寬度，就接起來；真的分段才空一行。
- 小標題（例如「押尾：」「9/10 Day 1」）用 `**粗體**` 或 `###`；條列用 `-` 或 `1.`。
- 畫掉的字：省略。插入的字（寫在行間的）：放到應在的位置。
- 看不清楚的字：寫 `〔?〕`；猜測的字：`〔猜測字?〕`。
- 插畫/貼紙：用一行 `> 〔插圖：簡短描述〕` 表示，不要長篇描述。
- 空白或只有插畫的頁：照實寫 `〔插圖：…〕` 或 `〔空白頁〕`。
- 頁面內容跨頁接續時，不要補完，只寫本頁看得到的。
- 第一行不要加「第 N 頁」之類的標題。

## 檢視器規格（`site/index.html`）
- 純靜態、無建置工具；`<script src="data.js">` 載入資料（file:// 也能開）。
- Markdown 用 cdnjs 的 marked.js 轉 HTML（marked 4.x 的 UMD 版）。
- 版面：左右兩欄，中間有**可拖動的分隔線**調整比例（存 localStorage）。
- 左欄：頁面圖片，適應欄寬；**滾輪/捏合縮放、按住拖曳平移**（縮放後），雙擊重設。
- 右欄：排版好的文字，字體 serif 系（"Noto Serif TC", "PingFang TC"），行距 1.9，字級可 A−/A/A+ 調整。
- 頂列：標題、頁碼「12 / 49」、上一頁/下一頁按鈕、跳頁輸入框、字級按鈕。
- 翻頁：按鈕、← → / PageUp PageDown 鍵、手機左右滑動（未縮放時）。
- URL hash `#p=12` 同步目前頁，可直接分享某一頁；重新整理保留頁碼。
- 預載下一頁圖片。
- 手機（< 768px）：上下排列（圖上、文下），分隔線改為上下拖動或隱藏。
- 深色模式（prefers-color-scheme）。

## 部署選項（待決定）
這是有真實姓名的私人日記，公開前請確認。
- **claude.ai Artifact**：預設私密，可再分享連結。最簡單。
- **GitHub Pages / Cloudflare Pages / Netlify**：公開網址，任何人都能看到。
- **區網**：`python3 -m http.server -d site 8000`，同 Wi-Fi 的人連 `http://<你的IP>:8000`。

---

# v2：多份文件 + 對比增強 + 公開部署

## 新目錄結構
```
notes-demo/
  PLAN.md  README.md  .gitignore
  pdfs/<slug>.pdf                 # 原始 PDF（不進 git）
  docs/<slug>/meta.json           # {"title": "海訓日誌", "subtitle": "113 秋季 C11", "pdf": "pdfs/<slug>.pdf", "order": 1}
  docs/<slug>/ocr/page_NNN.md     # OCR 結果（進 git，可人工修）
  tools/enhance.py                # enhance(img) 對比增強函式
  tools/render.py <slug>          # PDF -> site/docs/<slug>/pages/*.jpg（增強後）+ work/<slug>/ocr_img/*.png（增強後, 給 OCR）
  tools/build.py                  # 全部 docs/* -> site/docs/<slug>/data.js + site/library.js
  site/                           # GitHub Pages 發佈的內容（全部進 git）
    index.html                    # 文件列表 + 閱讀器（同一個檔）
    library.js                    # window.LIBRARY = [{slug,title,subtitle,pages,cover}]
    docs/<slug>/data.js           # window.DOC = {slug,title,subtitle,pages:[{n,img,w,h,md}]}
    docs/<slug>/pages/page_NNN.jpg
  work/                           # 暫存（不進 git）
  .github/workflows/pages.yml     # 把 site/ 部署到 GitHub Pages
```
slug 只用 ASCII 小寫、數字、連字號（例：`113-c11-autumn-sea-training`），因為會出現在網址。

## 對比增強（`tools/enhance.py`，已調好參數，照抄）
背景估計：縮小 1/8 → MaxFilter(7) → GaussianBlur(6) → 放大回原尺寸；`norm = rgb / bg * 255`；
levels：`black, white, gamma = 40, 250, 1.8`，`x = clip((norm-black)/(white-black),0,1) ** gamma`。
參考實作：`work/enhance_test.py`。網站圖 150 DPI、JPEG quality 82；OCR 圖 170 DPI PNG。

## 網站行為
- `index.html` 無參數 → **文件列表**：卡片格狀排列（封面縮圖＝第 1 頁、標題、副標、頁數），點擊進入閱讀器。
- `index.html?doc=<slug>#p=N` → 閱讀器（沿用現有功能）。動態插入 `<script src="docs/<slug>/data.js">` 載入資料（file:// 也能用）。
- 閱讀器頂列最左加「☰ 文件」返回列表的按鈕 + 一個 `<select>` 可直接切換文件；`<title>` = 文件標題。
- slug 不存在 → 顯示「找不到這份文件」並回到列表。
- localStorage 的分隔線比例、字級全域共用；每份文件記住最後閱讀頁（key `lastPage:<slug>`），從列表進入時若無 `#p=` 則跳到該頁。
