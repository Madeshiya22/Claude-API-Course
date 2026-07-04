from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field
from documents import docs

mcp = FastMCP("DocumentsServer")

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_documents() -> list[str]:
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_document(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]

@mcp.tool()
def read_document(name: str = Field(..., description="The exact name of the document to read, e.g., 'deposition.md'")) -> str:
    """Read the contents of a specific document."""
    if name not in docs:
        return f"Error: Document '{name}' not found."
    return docs[name]

@mcp.tool()
def edit_document(
    name: str = Field(..., description="The exact name of the document to edit"), 
    old_str: str = Field(..., description="The text to find and replace"),
    new_str: str = Field(..., description="The new text to replace the old text with")
) -> str:
    """Edit the contents of an existing document using find and replace."""
    if name not in docs:
        return f"Error: Document '{name}' not found."
    
    if old_str not in docs[name]:
        return f"Error: The string '{old_str}' was not found in document '{name}'."
        
    docs[name] = docs[name].replace(old_str, new_str)
    return f"Success: Document '{name}' was updated."

@mcp.prompt(
    name="format",
    description="Rewrite the contents of a document into Markdown format."
)
def format_document(
    doc_id: str = Field(
        description="Id of the document to format"
    )
) -> list[base.Message]:

    prompt = f"""
Your goal is to convert the following document into Markdown.

Document ID:
{doc_id}

Instructions:

- Read the document.
- Preserve the meaning.
- Use headings.
- Use bullet points where needed.
- Use tables if useful.
- Improve readability.
- After formatting, use the edit_document tool to overwrite the document.

Return only the final markdown.
"""

    return [
        base.UserMessage(prompt)
    ]

if __name__ == "__main__":
    mcp.run()
