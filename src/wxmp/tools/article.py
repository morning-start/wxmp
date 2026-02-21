import re
from pathlib import Path
from typing import Literal

from .file import save_html, save_markdown


def generate_yaml_front_matter(
    title: str = "",
    date_str: str = "",
    link: str = "",
    account_name: str = "",
    digest: str = "",
) -> str:
    """
    生成 YAML front matter 格式的元数据

    Args:
        title: 文章标题
        date_str: 日期字符串
        link: 文章链接
        account_name: 公众号名称
        digest: 文章摘要

    Returns:
        YAML front matter 字符串
    """
    yaml_front_matter = "---\n"
    if title:
        yaml_front_matter += f"title: {title}\n"
    if date_str:
        yaml_front_matter += f"date: {date_str}\n"
    if link:
        yaml_front_matter += f"link: {link}\n"
    if account_name:
        yaml_front_matter += f"account: {account_name}\n"
    if digest:
        yaml_front_matter += f"summary: {digest}\n"
    yaml_front_matter += "---\n"
    return yaml_front_matter


def save_article_content(
    html: str,
    save_path: Path,
    save_file: Literal["md", "html"] = "md",
    title: str = "",
    date_str: str = "",
    link: str = "",
    account_name: str = "",
    digest: str = "",
    min_file_size_kb: int = 3,
) -> bool:
    """
    保存文章内容到文件（带元数据和文件大小检查）

    Args:
        html: 文章HTML内容
        save_path: 保存路径
        save_file: 保存格式（md 或 html）
        title: 文章标题
        date_str: 日期字符串
        link: 文章链接
        account_name: 公众号名称
        digest: 文章摘要
        min_file_size_kb: 最小文件大小（KB），小于此值会被删除

    Returns:
        是否成功保存
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if save_path.exists():
        return True

    try:
        if save_file == "md":
            yaml_front_matter = generate_yaml_front_matter(
                title=title,
                date_str=date_str,
                link=link,
                account_name=account_name,
                digest=digest,
            )

            main_content = ""
            content_match = re.search(
                r'<div[^>]*id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL
            )

            if content_match:
                main_content = content_match.group(1)
            else:
                body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL)
                main_content = body_match.group(1) if body_match else html

            markdown_content = yaml_front_matter + html_to_markdown(main_content)
            save_markdown(markdown_content, save_path)
        elif save_file == "html":
            save_html(html, save_path)

        file_size = save_path.stat().st_size
        min_file_size_bytes = min_file_size_kb * 1024

        if file_size < min_file_size_bytes:
            save_path.unlink()
            return False

        return True

    except Exception as e:
        if save_path.exists():
            try:
                save_path.unlink()
            except:
                pass
        return False


def html_to_markdown(html: str) -> str:
    """
    Simple Regex-based HTML to Markdown converter.
    """
    # Remove style and script
    html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL)

    # Extract images: <img ... data-src="..."> or <img ... src="...">
    # Do this BEFORE removing any tags
    def replace_img(match):
        src = match.group(1) or match.group(2)
        return f"\n![]({src})\n"

    # Replace img tags with markdown images
    html = re.sub(r'<img[^>]+data-src="([^"]+)"[^>]*>', replace_img, html)
    html = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', replace_img, html)

    # Handle code blocks - <pre><code>...</code></pre> or <pre>...</pre>
    def replace_pre_code(match):
        code_content = match.group(1)
        # Remove inner <code> tags if present
        code_content = re.sub(
            r"<code[^>]*>(.*?)</code>", r"\1", code_content, flags=re.DOTALL
        )
        # Decode HTML entities in code
        code_content = (
            code_content.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
            .replace("&quot;", '"')
        )
        code_content = code_content.replace("&nbsp;", " ")
        return f"\n```\n{code_content}\n```\n"

    html = re.sub(r"<pre[^>]*>(.*?)</pre>", replace_pre_code, html, flags=re.DOTALL)

    # Handle inline code - <code>...</code>
    html = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", html, flags=re.DOTALL)

    # Remove lines that only contain HTML attributes (common in WeChat articles)
    html = re.sub(
        r"^\s*(class|data-|style|width|height|type|from|wx_fmt|data-ratio|data-type|data-w|data-imgfileid|data-aistatus|data-s)=[^>]*>\s*$",
        "",
        html,
        flags=re.MULTILINE,
    )

    # Headers
    for i in range(6, 0, -1):
        html = re.sub(f"<h{i}[^>]*>(.*?)</h{i}>", "#" * i + r" \1\n", html)

    # Paragraphs and Breaks
    html = re.sub(r"<p[^>]*>", "\n", html)
    html = re.sub(r"</p>", "\n", html)
    html = re.sub(r"<br\s*/?>", "\n", html)

    # Bold/Strong
    html = re.sub(r"<(b|strong)[^>]*>(.*?)</\1>", r"**\2**", html)

    # Lists (Simple)
    html = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", html)

    # Remove all remaining tags (including self-closing)
    html = re.sub(r"<[^>]+>", "", html)

    # Decode entities (basic)
    html = (
        html.replace("&nbsp;", " ")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
    )

    # Collapse multiple newlines and spaces
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r" +", " ", html)

    return html.strip()
