# PDF → Markdown 转换工具

基于 PyMuPDF4LLM 的本地 PDF 转换工具，将 PDF 文件转换为 Markdown 格式，**网页版 + 终端版**双模式。

---

## 功能特性

- 📄 PDF → Markdown 一键转换，保留文档结构
- 🌐 **网页版**：拖拽 PDF 到浏览器页面即可转换，界面友好
- ⌨️ **终端版**：命令行交互，适合批量操作
- 🔧 自动检测并安装依赖 `pymupdf4llm`
- 🖥️ 支持 macOS Apple Silicon (M1/M2/M3/M4) 和 Intel 芯片
- 🔒 **完全本地处理**，数据不出电脑

---

## 文件结构

```
PDF转MD工具/
├── 网页转换.py           ← 🌐 网页版（推荐）—— 浏览器拖拽转换
├── pdf_to_md.py          ← ⌨️ 终端版 —— 命令行交互
├── 启动转换.command       ← 🚀 启动入口 —— 自动选择网页版或终端版
└── 📄 PDF转MD.webloc     ← 🔖 浏览器书签 —— 服务器运行后双击直达
```

---

## 快速开始

### 方式一：终端运行（最可靠）

1. 打开 **终端**（`Command + 空格` → 输入 `Terminal`）
2. 粘贴以下命令并回车：

```bash
python3 ~/Desktop/AI学习/PDF转MD工具/网页转换.py
```

3. 浏览器自动打开转换页面，拖入 PDF 文件即可

### 方式二：终端运行命令行版

```bash
python3 ~/Desktop/AI学习/PDF转MD工具/pdf_to_md.py /path/to/your.pdf
```

---

## 依赖要求

| 依赖 | 说明 |
|------|------|
| Python 3.9+ | 推荐通过 Homebrew 安装（`brew install python3`） |
| pymupdf4llm | 首次运行自动安装 |

---

## 输出路径

- **网页版**：文件保存到工作区根目录（`AI学习/`）及浏览器下载文件夹
- **终端版**：文件保存到 `PDF转MD工具/output/`

---

## 常见问题

### Q: 双击 `启动转换.command` 没反应？

macOS 26 加强了安全限制，未签名脚本无法通过双击启动。请使用**方式一**在终端运行，或将脚本右键 → 打开方式 → 终端。

### Q: 提示找不到 Python？

```bash
brew install python3
```

### Q: 端口被占用？

脚本会自动尝试 8765-8774 端口，如全部占用可手动指定端口后修改 `网页转换.py` 中的 `PORT` 变量。

### Q: 转换结果不完整或格式错乱？

PyMuPDF4LLM 对排版复杂的 PDF（扫描件、图片为主的 PDF）效果有限。复杂表格或图片密集型文档建议使用 `/pdf-converter` skill（基于 MinerU）。

---

## 技术原理

```
PDF 文件 → PyMuPDF4LLM 解析 → Markdown 文本 → 保存到本地
                ↑
         网页版：Flask 风格 HTTP 本地服务器 + 浏览器前端
         终端版：交互式命令行
```
