#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 转 Markdown 工具
基于 PyMuPDF4LLM，将 PDF 文件转换为 Markdown 格式
"""

import sys
import os
import shutil
from pathlib import Path

# 工作区根目录（脚本所在目录的上一级）
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = WORKSPACE_DIR / "output"


def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import pymupdf4llm
        return True
    except ImportError:
        return False


def install_dependencies():
    """安装缺失的依赖"""
    import subprocess
    print("⏳ 正在安装依赖 pymupdf4llm ...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--break-system-packages", "pymupdf4llm", "-q"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 依赖安装失败: {result.stderr}")
        return False
    print("✅ 依赖安装完成")
    return True


def convert_pdf_to_md(pdf_path: str, output_dir: str = None) -> str:
    """
    将 PDF 文件转换为 Markdown

    Args:
        pdf_path: PDF 文件的完整路径
        output_dir: 输出目录，默认为工作区的 output 文件夹

    Returns:
        生成的 Markdown 文件路径
    """
    import pymupdf4llm

    pdf_path = Path(pdf_path).expanduser().resolve()

    # 验证文件存在
    if not pdf_path.exists():
        raise FileNotFoundError(f"找不到文件: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"不是 PDF 文件: {pdf_path.suffix}")

    # 确定输出目录
    if output_dir:
        out_dir = Path(output_dir).expanduser().resolve()
    else:
        out_dir = OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    pdf_name = pdf_path.stem
    # 清理文件名中的多余点号
    pdf_name = pdf_name.replace("..", ".")
    output_file = out_dir / f"{pdf_name}.md"

    # 显示文件信息
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"📄 源文件: {pdf_path}")
    print(f"📏 大小: {file_size_mb:.1f} MB")
    print(f"🔄 正在转换，请稍候...")

    # 执行转换
    md_text = pymupdf4llm.to_markdown(str(pdf_path))

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_text)

    output_size_kb = output_file.stat().st_size / 1024
    print(f"✅ 转换完成！")
    print(f"📝 输出文件: {output_file}")
    print(f"📏 输出大小: {output_size_kb:.1f} KB")
    print(f"📊 字符数: {len(md_text):,}")

    return str(output_file)


def main():
    print("=" * 50)
    print("   PDF → Markdown 转换工具")
    print("=" * 50)
    print()

    # 检查依赖
    if not check_dependencies():
        print("⚠️  缺少必要依赖，正在自动安装...")
        if not install_dependencies():
            print("❌ 依赖安装失败，请手动运行: pip3 install --break-system-packages pymupdf4llm")
            input("按回车键退出...")
            sys.exit(1)

    # 获取 PDF 路径
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("请拖入 PDF 文件或输入文件路径: ").strip().strip("'").strip('"')

    if not pdf_path:
        print("❌ 未提供文件路径，已退出。")
        input("按回车键退出...")
        sys.exit(1)

    # 执行转换
    try:
        output_file = convert_pdf_to_md(pdf_path)
        print()
        print(f"🎉 转换成功！文件已保存至: {output_file}")
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

    print()
    input("按回车键退出...")


if __name__ == "__main__":
    main()
