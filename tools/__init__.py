"""
Custom tools for Email AI Agent
"""

from .mermaid_generator import (
    create_mermaid_diagram_tool,
    generate_inbox_diagram,
    MermaidInput,
    CategoryNode
)

__all__ = [
    "create_mermaid_diagram_tool",
    "generate_inbox_diagram",
    "MermaidInput",
    "CategoryNode"
]
