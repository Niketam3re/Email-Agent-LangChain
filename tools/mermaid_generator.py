"""
Mermaid Diagram Generator Tool
Generates Mermaid diagrams from email category hierarchies
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class CategoryNode(BaseModel):
    """Represents a category node in the hierarchy"""
    id: str
    name: str
    parent_id: str | None = None
    email_count: int = 0
    subcategories: List['CategoryNode'] = Field(default_factory=list)


class MermaidInput(BaseModel):
    """Input schema for Mermaid diagram generation"""
    categories: List[Dict[str, Any]] = Field(
        description="List of category dictionaries with id, name, parent_id, email_count"
    )


def build_category_tree(categories: List[Dict[str, Any]]) -> List[CategoryNode]:
    """
    Build a tree structure from flat category list

    Args:
        categories: Flat list of category dictionaries

    Returns:
        List of root CategoryNode objects with nested subcategories
    """
    # Create a mapping of id to CategoryNode
    nodes_map: Dict[str, CategoryNode] = {}

    for cat in categories:
        node = CategoryNode(
            id=str(cat.get('id', '')),
            name=cat.get('name', ''),
            parent_id=str(cat.get('parent_id')) if cat.get('parent_id') else None,
            email_count=cat.get('email_count', 0)
        )
        nodes_map[node.id] = node

    # Build the tree by linking parents and children
    root_nodes = []
    for node in nodes_map.values():
        if node.parent_id and node.parent_id in nodes_map:
            # Add to parent's subcategories
            parent = nodes_map[node.parent_id]
            parent.subcategories.append(node)
        else:
            # This is a root node
            root_nodes.append(node)

    return root_nodes


def generate_mermaid_nodes(
    node: CategoryNode,
    mermaid_lines: List[str],
    node_counter: Dict[str, int]
) -> str:
    """
    Recursively generate Mermaid diagram nodes

    Args:
        node: Current CategoryNode
        mermaid_lines: List to append Mermaid syntax lines to
        node_counter: Counter for unique node IDs

    Returns:
        The Mermaid node ID for this node
    """
    # Generate unique node ID
    current_count = node_counter.get('count', 0)
    node_counter['count'] = current_count + 1
    node_id = f"node{current_count}"

    # Create node label with name and email count
    label = f"{node.name}"
    if node.email_count > 0:
        label += f" ({node.email_count})"

    # Add node definition
    mermaid_lines.append(f'    {node_id}["{label}"]')

    # Process subcategories
    for subcat in node.subcategories:
        subcat_id = generate_mermaid_nodes(subcat, mermaid_lines, node_counter)
        # Add edge from parent to child
        mermaid_lines.append(f'    {node_id} --> {subcat_id}')

    return node_id


def create_mermaid_diagram(categories: List[Dict[str, Any]]) -> str:
    """
    Generate a Mermaid diagram from category hierarchy

    Args:
        categories: List of category dictionaries

    Returns:
        Mermaid diagram as a string
    """
    if not categories:
        return "```mermaid\ngraph TD\n    inbox[Inbox - No categories yet]\n```"

    # Build category tree
    root_nodes = build_category_tree(categories)

    # Start building Mermaid diagram
    mermaid_lines = [
        "```mermaid",
        "graph TD"
    ]

    # Add inbox as root node
    mermaid_lines.append('    inbox["📬 Inbox"]')

    # Counter for unique node IDs
    node_counter = {'count': 0}

    # Generate nodes for each root category
    for root in root_nodes:
        root_id = generate_mermaid_nodes(root, mermaid_lines, node_counter)
        # Connect inbox to root category
        mermaid_lines.append(f'    inbox --> {root_id}')

    # Add styling
    mermaid_lines.extend([
        "",
        "    classDef inboxStyle fill:#4A90E2,stroke:#2E5C8A,color:#fff",
        "    class inbox inboxStyle"
    ])

    mermaid_lines.append("```")

    return "\n".join(mermaid_lines)


@tool("create_mermaid_diagram", args_schema=MermaidInput, return_direct=False)
def create_mermaid_diagram_tool(categories: List[Dict[str, Any]]) -> str:
    """
    Generate a Mermaid diagram visualizing the email inbox category hierarchy.

    This tool takes a list of email categories and creates a visual tree diagram
    showing how categories are organized, including email counts for each category.

    Args:
        categories: List of category dictionaries, each containing:
            - id: Unique identifier
            - name: Category name
            - parent_id: Parent category ID (None for root categories)
            - email_count: Number of emails in this category

    Returns:
        A Mermaid diagram in markdown format showing the inbox structure

    Example:
        ```python
        categories = [
            {"id": "1", "name": "Work", "parent_id": None, "email_count": 45},
            {"id": "2", "name": "Project A", "parent_id": "1", "email_count": 20},
            {"id": "3", "name": "Hockey", "parent_id": None, "email_count": 30}
        ]
        diagram = create_mermaid_diagram_tool(categories)
        ```
    """
    return create_mermaid_diagram(categories)


# Standalone function for direct use
def generate_inbox_diagram(categories: List[Dict[str, Any]]) -> str:
    """
    Standalone function to generate Mermaid diagram
    Can be used without LangChain tool wrapper

    Args:
        categories: List of category dictionaries

    Returns:
        Mermaid diagram string
    """
    return create_mermaid_diagram(categories)


if __name__ == "__main__":
    # Test the Mermaid generator
    sample_categories = [
        {"id": "1", "name": "Work", "parent_id": None, "email_count": 45},
        {"id": "2", "name": "Project Alpha", "parent_id": "1", "email_count": 20},
        {"id": "3", "name": "Project Beta", "parent_id": "1", "email_count": 15},
        {"id": "4", "name": "Meetings", "parent_id": "1", "email_count": 10},
        {"id": "5", "name": "Hockey", "parent_id": None, "email_count": 30},
        {"id": "6", "name": "Team A", "parent_id": "5", "email_count": 18},
        {"id": "7", "name": "Team B", "parent_id": "5", "email_count": 12},
        {"id": "8", "name": "Personal", "parent_id": None, "email_count": 25},
        {"id": "9", "name": "Family", "parent_id": "8", "email_count": 15},
        {"id": "10", "name": "Friends", "parent_id": "8", "email_count": 10},
    ]

    diagram = generate_inbox_diagram(sample_categories)
    print(diagram)
