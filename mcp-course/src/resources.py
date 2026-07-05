from src.server import mcp
from src.tools import docs  # Importing shared state from tools

# Add some initial mock data for the resources lecture demonstration
# if it's currently empty, so we have something to list and fetch!
if not docs:
    docs.update({
        "report.pdf": "This report details the Q3 financial review and risk analysis.",
        "plan.md": "The project plan outlines upcoming milestones and deadlines for the MCP integration.",
        "spec.txt": "Technical specifications for the new FastMCP API endpoints."
    })

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    """List all available documents."""
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    """Fetch the content of a specific document by its ID."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")
    
    return docs[doc_id]
