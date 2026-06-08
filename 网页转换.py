#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF → Markdown 网页转换工具
双击 PDF 拖入浏览器页面即可转换，文件自动保存到工作区
"""

import sys
import os
import json
import time
import webbrowser
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 路径配置
PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = PROJECT_DIR.parent   # 工作区 = AI学习/
OUTPUT_DIR = WORKSPACE_DIR           # 输出直接到工作区根目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8765

# ============================================================
# HTML 网页界面
# ============================================================
HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF → Markdown 转换工具</title>
<style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Helvetica Neue", sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        min-height: 100vh;
        display: flex; align-items: center; justify-content: center;
        color: #e2e8f0;
    }
    .container { text-align: center; max-width: 600px; padding: 40px 24px; }
    .icon { font-size: 56px; margin-bottom: 16px; }
    h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.02em; }
    .subtitle { color: #94a3b8; font-size: 15px; margin-bottom: 36px; }
    .drop-zone {
        border: 2px dashed #475569; border-radius: 16px; padding: 60px 30px;
        cursor: pointer; transition: all 0.25s ease;
        background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px);
        margin-bottom: 24px; position: relative;
    }
    .drop-zone:hover, .drop-zone.drag-over {
        border-color: #38bdf8; background: rgba(56, 189, 248, 0.08);
        transform: translateY(-2px); box-shadow: 0 8px 30px rgba(56, 189, 248, 0.12);
    }
    .drop-zone-text { font-size: 16px; color: #cbd5e1; }
    .drop-zone-hint { font-size: 13px; color: #64748b; margin-top: 8px; }
    #fileInput { display: none; }

    .status {
        margin-top: 20px; padding: 14px 20px; border-radius: 12px;
        font-size: 14px; display: none; align-items: center; gap: 10px; justify-content: center;
    }
    .status.show { display: flex; }
    .status.uploading { background: rgba(250, 204, 21, 0.12); color: #facc15; }
    .status.converting { background: rgba(56, 189, 248, 0.12); color: #38bdf8; }
    .status.success { background: rgba(52, 211, 153, 0.12); color: #34d399; }
    .status.error { background: rgba(248, 113, 113, 0.12); color: #f87171; }

    .spinner {
        width: 20px; height: 20px; border: 2.5px solid currentColor;
        border-top-color: transparent; border-radius: 50%;
        animation: spin 0.7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .btn {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 12px 28px; border-radius: 12px; font-size: 15px;
        font-weight: 600; cursor: pointer; border: none;
        transition: all 0.2s ease; text-decoration: none;
    }
    .btn-download {
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        color: white; box-shadow: 0 4px 16px rgba(56, 189, 248, 0.25);
    }
    .btn-download:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(56, 189, 248, 0.35); }

    .footer { margin-top: 48px; font-size: 12px; color: #475569; }
    .output-path { font-size: 12px; color: #64748b; margin-top: 6px; }
</style>
</head>
<body>

<div class="container">
    <div class="icon">📄</div>
    <h1>PDF 转 Markdown</h1>
    <p class="subtitle">拖拽 PDF 文件到下方区域，自动转换并保存到工作区</p>

    <div class="drop-zone" id="dropZone">
        <div class="drop-zone-text">📂 拖拽 PDF 文件到此处</div>
        <div class="drop-zone-hint">或点击选择文件 · 自动保存到 AI学习 文件夹</div>
    </div>
    <input type="file" id="fileInput" accept=".pdf">

    <div class="status" id="status">
        <div class="spinner" id="spinner"></div>
        <span id="statusText"></span>
    </div>

    <div id="resultArea"></div>
    <div class="footer">基于 PyMuPDF4LLM · 本地处理，数据不出电脑</div>
</div>

<script>
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const status = document.getElementById('status');
const statusText = document.getElementById('statusText');
const spinner = document.getElementById('spinner');
const resultArea = document.getElementById('resultArea');

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

function setStatus(type, text, showSpin) {
    status.className = 'status show ' + type;
    statusText.textContent = text;
    spinner.style.display = showSpin ? 'block' : 'none';
}

async function handleFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        setStatus('error', '⚠️ 请选择 PDF 文件', false);
        setTimeout(() => status.classList.remove('show'), 3000);
        return;
    }

    setStatus('uploading', '📤 上传中: ' + file.name, true);
    const formData = new FormData();
    formData.append('pdf', file);

    try {
        const resp = await fetch('/convert', { method: 'POST', body: formData });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '服务器错误');
        }

        setStatus('converting', '🔄 正在转换中，请稍候...', true);

        const data = await resp.json();
        const outputName = data.filename;
        const outputPath = data.output_path;
        const charCount = data.char_count;

        // 触发浏览器下载
        const blob = new Blob([data.content], { type: 'text/markdown; charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = outputName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        setStatus('success', '✅ 转换完成！已保存: ' + outputName + ' (' + charCount.toLocaleString() + ' 字符)', false);
        resultArea.innerHTML = '<p class="output-path">📂 文件位置: ' + outputPath + '</p>';
    } catch (err) {
        setStatus('error', '❌ 转换失败: ' + err.message, false);
    }
}
</script>

</body>
</html>
"""


# ============================================================
# HTTP 请求处理器
# ============================================================
class PDFConverterHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != '/convert':
            self.send_json_error(404, '未找到')
            return

        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_json_error(400, '不支持的请求格式')
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            # 解析 multipart
            boundary = content_type.split('boundary=')[1].encode()
            parts = body.split(b'--' + boundary)

            pdf_data = None
            original_name = 'document.pdf'

            for part in parts:
                if b'Content-Disposition' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end == -1:
                        continue
                    header = part[:header_end].decode('utf-8', errors='ignore')
                    data = part[header_end + 4:]
                    if data.endswith(b'\r\n'):
                        data = data[:-2]

                    if 'name="pdf"' in header:
                        pdf_data = data
                        if 'filename="' in header:
                            fn_start = header.index('filename="') + 10
                            fn_end = header.index('"', fn_start)
                            original_name = header[fn_start:fn_end]

            if not pdf_data:
                self.send_json_error(400, '未收到 PDF 文件')
                return

            # 保存临时 PDF
            temp_pdf = OUTPUT_DIR / f"_temp_{int(time.time())}.pdf"
            with open(temp_pdf, 'wb') as f:
                f.write(pdf_data)

            # 执行转换
            try:
                import pymupdf4llm
                md_text = pymupdf4llm.to_markdown(str(temp_pdf))
            except ImportError:
                self.send_json_error(500, '缺少 pymupdf4llm 依赖')
                return
            finally:
                temp_pdf.unlink(missing_ok=True)

            # 保存到工作区
            stem = Path(original_name).stem
            output_name = f"{stem}.md"
            output_file = OUTPUT_DIR / output_name

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_text)

            print(f'✅ 转换完成: {original_name} → {output_file}')

            # 返回 JSON（包含文件内容和保存路径）
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'filename': output_name,
                'output_path': str(output_file),
                'char_count': len(md_text),
                'content': md_text,
            }, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_json_error(500, str(e))

    def send_json_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        print(f'  {args[0]}')


# ============================================================
# 启动逻辑
# ============================================================
def main():
    no_browser = '--no-browser' in sys.argv

    print('=' * 50)
    print('   PDF → Markdown 网页转换工具')
    print('=' * 50)
    print()

    # 检查依赖
    try:
        import pymupdf4llm  # noqa: F401
    except ImportError:
        print('⚠️  缺少 pymupdf4llm，正在安装...')
        import subprocess
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--break-system-packages', 'pymupdf4llm', '-q'],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f'❌ 安装失败: {r.stderr}')
            input('按回车键退出...')
            sys.exit(1)
        print('✅ 安装完成')
        print()

    # 启动服务器
    server = None
    for port in range(PORT, PORT + 10):
        try:
            server = HTTPServer(('127.0.0.1', port), PDFConverterHandler)
            break
        except OSError:
            continue

    if server is None:
        print(f'❌ 端口 {PORT}-{PORT+9} 全部被占用')
        input('按回车键退出...')
        sys.exit(1)

    url = f'http://127.0.0.1:{server.server_address[1]}'
    print(f'🌐 地址: {url}')
    print(f'📂 输出: {OUTPUT_DIR}')
    print()

    if not no_browser:
        def open_browser():
            time.sleep(0.5)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()
        print('✅ 浏览器已打开，拖拽 PDF 即可转换')
    else:
        print('✅ 后台服务已启动')

    print('💡 按 Ctrl+C 停止')
    print('=' * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n👋 已停止')
        server.shutdown()


if __name__ == '__main__':
    main()
