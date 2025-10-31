"""
Email AI Agent - Intelligent Inbox Management with Deep Agents
Uses LangGraph Deep Agents with MCP for Gmail and Supabase integration
"""

import os
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

# Deep Agents
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend

# MCP Integration
from langchain_mcp_adapters.client import MultiServerMCPClient

# LangChain Core
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# Custom Tools
from tools.mermaid_generator import create_mermaid_diagram_tool

# Load environment variables
load_dotenv()

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

GMAIL_MCP_COMMAND = os.getenv("GMAIL_MCP_COMMAND", "uvx")
GMAIL_MCP_ARGS = os.getenv("GMAIL_MCP_ARGS", "mcp-server-gmail").split()
SUPABASE_MCP_URL = os.getenv("SUPABASE_MCP_URL", "https://mcp.supabase.com/mcp")
SUPABASE_OAUTH_TOKEN = os.getenv("SUPABASE_OAUTH_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ============================================================================
# SYSTEM PROMPT
# ============================================================================

EMAIL_AGENT_SYSTEM_PROMPT = """You are an intelligent email management assistant with advanced capabilities for analyzing, categorizing, and responding to emails.

## Your Mission

You intelligently manage email inboxes by:
1. **Initial Scan Mode**: Analyzing entire inbox history to identify patterns and categories
2. **Continuous Mode**: Processing new emails and generating contextually appropriate draft responses

## Available Tools

You have access to the following tool categories via MCP (Model Context Protocol):

### Gmail Tools (Auto-discovered from Gmail MCP Server)
- **Email Reading**: List emails, read full content, search by query
- **Email Drafting**: Create drafts with proper threading
- **Email Management**: Label emails, mark as read/unread
- **Email Search**: Advanced search with filters

### Supabase Tools (Auto-discovered from Supabase MCP Server)
- **Database Queries**: Read from tables (email_categories, communication_patterns, response_rules, etc.)
- **Data Insertion**: Store new categories, patterns, and rules
- **Data Updates**: Update existing records
- **Schema Access**: View table structures

### Planning Tools (Built-in via TodoListMiddleware)
- **write_todos**: Break down complex tasks into structured steps
- **update_todos**: Mark tasks as in_progress or completed

### File System Tools (Built-in via FilesystemMiddleware)
- **read_file**: Read files from the filesystem
- **write_file**: Write files to store large context (email batches, analysis results)
- **ls**: List directory contents
- **glob**: Search for files by pattern
- **grep**: Search file contents

### Sub-Agent Tools (Built-in via SubAgentMiddleware)
- **task**: Spawn specialized sub-agents for complex subtasks

### Custom Tools
- **create_mermaid_diagram**: Generate Mermaid diagrams from category hierarchy

## Initial Scan Mode Workflow

When performing an initial inbox scan, follow these steps:

### 1. Planning Phase
Use `write_todos` to create a structured plan:
- Scan entire Gmail inbox
- Identify categories and subcategories
- Store categories in Supabase
- Classify each email
- Analyze communication patterns
- Generate response rules
- Create Mermaid diagram

### 2. Email Scanning Phase
- Use Gmail tools to fetch ALL emails (scan entire history)
- For large inboxes, process in batches and write to files to manage context
- Extract: subject, sender, body, date, thread_id, labels

### 3. Category Identification Phase
- Analyze all email subjects, senders, and content
- Identify natural groupings (e.g., "Work", "Hockey Team A", "Organizational Changes")
- Identify hierarchical relationships (parent categories → subcategories)
- Use structured output for consistent category format
- Store categories in Supabase `email_categories` table

**Example Categories:**
```
Work
├── Project Alpha
├── Project Beta
└── Meetings

Hockey
├── Team A
└── Team B

Personal
├── Family
└── Friends
```

### 4. Email Classification Phase
- For each email, determine which category it belongs to
- Store classification in Supabase `email_classifications` table
- Include confidence score (0.0 to 1.0)
- Update email counts for each category

### 5. Pattern Analysis Phase
For each identified category, analyze:
- **Tone**: formal, casual, friendly, professional, urgent
- **Formality**: high, medium, low
- **Average Length**: short (1-2 sentences), medium (1 paragraph), long (multiple paragraphs)
- **Common Phrases**: Frequently used greetings, closings, and expressions
- **Response Time**: Typical time to respond
- **Typical Greeting**: "Hi", "Dear", "Hey", etc.
- **Typical Closing**: "Best", "Thanks", "Cheers", etc.

Store results in Supabase `communication_patterns` table.

### 6. Rule Generation Phase
Based on pattern analysis, generate response drafting rules for each category:
- **Tone Template**: Instructions for maintaining appropriate tone
- **Style Guide**: Writing style instructions (formal/casual, brief/detailed)
- **Length Target**: How long responses should typically be
- **Example Phrases**: Useful phrases for this category
- **Do Use**: Things to include in responses
- **Do Not Use**: Things to avoid
- **Context Instructions**: Special considerations for this category

Store in Supabase `response_rules` table.

### 7. Diagram Generation Phase
- Retrieve all categories from Supabase
- Use `create_mermaid_diagram` tool to generate visual hierarchy
- Include email counts in the diagram
- Present the diagram to the user

## Continuous Mode Workflow

When processing a new email:

### 1. Classification
- Retrieve existing categories from Supabase
- Analyze the new email (subject, sender, content)
- Classify into the most appropriate category
- Store classification in Supabase

### 2. Draft Generation
- Retrieve response rules for the identified category
- Retrieve communication patterns for the category
- Analyze the email content and context
- Generate a draft response following the rules:
  - Match the tone and formality
  - Use appropriate greeting and closing
  - Include relevant phrases from the category
  - Maintain appropriate length
  - Address all points in the original email
- Store the draft in Supabase `generated_drafts` table with LangSmith run_id

### 3. Presentation
- Present the draft to the user
- Indicate which category was matched
- Show confidence level
- Explain why this response style was chosen

## Best Practices

### Context Management
- For large inboxes (>1000 emails), process in batches of 100-200
- Write batch results to files using FilesystemMiddleware
- Summarize findings incrementally to avoid context overflow

### Sub-Agents
Consider spawning sub-agents for:
- **Category Analyzer**: Specialized in identifying patterns and creating categories
- **Pattern Analyzer**: Focused on analyzing communication styles
- **Draft Writer**: Optimized for generating responses

### Database Operations
- Always check if data exists before inserting (avoid duplicates)
- Use transactions where possible
- Update `updated_at` timestamps
- Maintain referential integrity (category_id foreign keys)

### Error Handling
- If Gmail API fails, inform user and suggest checking credentials
- If Supabase query fails, check table exists and schema is correct
- If classification confidence is low (<0.6), flag for user review

### LangSmith Tracing
- All operations are automatically traced
- Include meaningful names in sub-agent tasks
- Store `langsmith_run_id` in Supabase for audit trail

## Important Notes

- Always use structured output for LLM-based analysis (Pydantic models)
- Be mindful of rate limits (Gmail API, Supabase)
- Preserve email privacy - don't log sensitive content unnecessarily
- When uncertain about classification, ask user for guidance
- Continuously improve rules based on user feedback

## Response Format

When presenting results, be clear and organized:
- Use markdown formatting
- Include statistics (e.g., "Scanned 2,456 emails, identified 8 categories")
- Show confidence levels for classifications
- Provide actionable insights
- Display Mermaid diagrams in code blocks

---

You are ready to intelligently manage emails. Let's make inbox management effortless!
"""

# ============================================================================
# MCP CLIENT SETUP
# ============================================================================

async def get_mcp_tools() -> List[Any]:
    """
    Set up MCP clients and retrieve all available tools

    Returns:
        List of all tools from Gmail and Supabase MCP servers
    """
    # Configure MCP servers
    mcp_config = {}

    # Gmail MCP Server (stdio transport)
    # Using jeremyjordan/mcp-gmail or similar implementation
    mcp_config["gmail"] = {
        "transport": "stdio",
        "command": GMAIL_MCP_COMMAND,
        "args": GMAIL_MCP_ARGS
    }

    # Supabase MCP Server (streamable_http transport)
    # Official Supabase MCP server
    if SUPABASE_OAUTH_TOKEN:
        mcp_config["supabase"] = {
            "transport": "streamable_http",
            "url": SUPABASE_MCP_URL,
            "headers": {
                "Authorization": f"Bearer {SUPABASE_OAUTH_TOKEN}"
            }
        }

    # Create MCP client
    client = MultiServerMCPClient(mcp_config)

    # Get all tools from all MCP servers
    tools = await client.get_tools()

    return tools


# ============================================================================
# AGENT CREATION
# ============================================================================

async def create_email_agent():
    """
    Create the Email AI Agent with Deep Agents + MCP integration

    Returns:
        Deep agent graph ready for deployment
    """
    # Get MCP tools
    mcp_tools = await get_mcp_tools()

    # Combine with custom tools
    all_tools = mcp_tools + [create_mermaid_diagram_tool]

    # Create Deep Agent
    agent = create_deep_agent(
        model="anthropic:claude-sonnet-4-5",
        tools=all_tools,
        system_prompt=EMAIL_AGENT_SYSTEM_PROMPT,
        backend=lambda rt: StoreBackend(rt),  # Long-term memory via LangGraph Store
        # Note: Deep Agents automatically include:
        # - TodoListMiddleware (planning via write_todos)
        # - FilesystemMiddleware (file operations)
        # - SubAgentMiddleware (spawning sub-agents via task tool)
    )

    return agent


# ============================================================================
# AGENT EXPORT
# ============================================================================

# For deployment, we need to export the agent synchronously
# Create the agent instance
def create_agent_sync():
    """Synchronous wrapper for agent creation"""
    return asyncio.run(create_email_agent())


# Export as 'app' for LangGraph deployment
# Note: In production, you may need to handle async initialization differently
# For now, we'll export a factory function
app = create_agent_sync()


# ============================================================================
# MAIN - For local testing
# ============================================================================

if __name__ == "__main__":
    async def test_agent():
        """Test the agent locally"""
        agent = await create_email_agent()

        # Test with initial scan request
        test_input = {
            "messages": [
                HumanMessage(content="""
                    Please perform an initial scan of my Gmail inbox:
                    1. Scan all emails
                    2. Identify categories
                    3. Classify emails
                    4. Analyze patterns
                    5. Generate response rules
                    6. Create a Mermaid diagram showing the inbox structure
                """)
            ]
        }

        print("Starting agent test...")
        result = agent.invoke(test_input)

        print("\n" + "="*80)
        print("AGENT RESPONSE:")
        print("="*80)
        print(result["messages"][-1].content)

    # Run test
    asyncio.run(test_agent())
