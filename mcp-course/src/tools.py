from src.server import mcp

# In-memory document storage
docs = {}

@mcp.tool()
def read_document(doc_id: str) -> str:
    """
    Read the contents of a document by its ID.
    """
    if doc_id in docs:
        return docs[doc_id]
    return f"Error: Document '{doc_id}' not found."

@mcp.tool()
def edit_document(doc_id: str, content: str) -> str:
    """
    Create or edit a document with the specified ID and content.
    """
    docs[doc_id] = content
    return f"Success: Document '{doc_id}' has been saved."
