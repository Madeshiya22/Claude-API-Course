from pydantic import Field
from mcp.server.fastmcp.prompts import base
from src.server import mcp

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
):
    prompt = f"""
Your goal is to reformat a document into Markdown.

Document:
{doc_id}

Use headings, bullet points, tables, etc.
Use the edit_document tool after reading the document.
"""

    return [
        base.UserMessage(prompt)
    ]
