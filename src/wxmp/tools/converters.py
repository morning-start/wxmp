import re
from abc import ABC, abstractmethod


class HTMLConverter(ABC):
    """HTML 转换器抽象基类"""

    @abstractmethod
    def convert(self, html: str) -> str:
        """
        将 HTML 转换为目标格式

        Args:
            html: HTML 内容

        Returns:
            转换后的内容
        """
        pass


class HTMLToMarkdownConverter(HTMLConverter):
    """HTML 转 Markdown 转换器"""

    def convert(self, html: str) -> str:
        """
        将 HTML 转换为 Markdown

        Args:
            html: HTML 内容

        Returns:
            Markdown 格式内容
        """
        return self._html_to_markdown(html)

    def _html_to_markdown(self, html: str) -> str:
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


class HTMLToTextConverter(HTMLConverter):
    """HTML 转纯文本转换器"""

    def convert(self, html: str) -> str:
        """
        将 HTML 转换为纯文本

        Args:
            html: HTML 内容

        Returns:
            纯文本内容
        """
        # Remove style and script
        text = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.DOTALL)
        text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL)

        # Replace common block elements with newlines
        text = re.sub(r"</(p|div|h[1-6]|li|tr)>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<(br|/tr)\s*/?>", "\n", text, flags=re.IGNORECASE)

        # Remove all remaining tags
        text = re.sub(r"<[^>]+>", "", text)

        # Decode entities
        text = (
            text.replace("&nbsp;", " ")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
        )

        # Collapse multiple newlines and spaces
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" +", " ", text)

        return text.strip()
