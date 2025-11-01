"""
Output formatting utilities for final package generation.
"""


class OutputFormatter:
    """Formats content into various output formats."""
    
    @staticmethod
    def format_markdown(story: str, title: str = "Generated Story") -> str:
        """Format story as Markdown."""
        lines = [f"# {title}\n"]
        paragraphs = story.split('\n\n')
        for para in paragraphs:
            lines.append(para.strip())
            lines.append("")  # Empty line between paragraphs
        return "\n".join(lines)
    
    @staticmethod
    def format_html(story: str, title: str = "Generated Story") -> str:
        """Format story as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        p {{
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
"""
        paragraphs = story.split('\n\n')
        for para in paragraphs:
            html += f"    <p>{para.strip()}</p>\n"
        
        html += """</body>
</html>"""
        return html
    
    @staticmethod
    def format_json_structured(story: str, metadata: dict) -> dict:
        """Format story as structured JSON data."""
        return {
            "title": metadata.get("title", "Generated Story"),
            "content": story,
            "metadata": metadata
        }

