# LangGraph Development Principles

**Last Updated: October 2025 - LangGraph 1.0 & LangChain 1.0 Release**

If you are coding with LangGraph, follow these principles and patterns.

## 🎉 Major October 2025 Updates

### LangGraph 1.0 & LangChain 1.0 (Released October 22, 2025)
- **First stable major releases** - No breaking changes until 2.0
- **Product Renaming**: "LangGraph Platform" → "LangSmith Deployment"
- **Python 3.10+ required** (Python 3.9 support dropped)

### Critical API Changes:
```python
# OLD (Deprecated):
from langgraph.prebuilt import create_react_agent

# NEW (LangChain 1.0):
from langchain.agents import create_agent

# All langgraph.prebuilt functions moved to langchain.agents
```

### New Middleware System
LangChain 1.0 introduces a powerful **Middleware architecture** for fine-grained control over agent execution:
- `before_model`: Runs before LLM calls
- `after_model`: Runs after LLM calls  
- `modify_model_request`: Modify tools, prompts, messages before LLM calls
- Composable: Stack multiple middleware sequentially

See the [Middleware System](#middleware-system) section below for details.

## Critical Structure Requirements

### MANDATORY FIRST STEP
Before creating any files, **always search the codebase** for existing LangGraph-related files:
- Files with names like: `graph.py`, `main.py`, `app.py`, `agent.py`, `workflow.py`
- Files containing: `.compile()`, `StateGraph`, `create_react_agent`, `app =`, graph exports
- Any existing LangGraph imports or patterns

**If any LangGraph files exist**: Follow the existing structure exactly. Do not create new agent.py files.

**Only create agent.py when**: Building from completely empty directory with zero existing LangGraph files.

- When starting from scratch, ensure all of the following:
  1. `agent.py` at project root with compiled graph exported as `app`
  2. `langgraph.json` configuration file in the same directory as the graph
  3. Proper state management defined with `TypedDict` or Pydantic `BaseModel`
  4. Test small components before building complex graphs

## Deployment-First Principles

**CRITICAL**: All LangGraph agents should be written for DEPLOYMENT unless otherwise specified.

**NOTE**: As of October 2025, "LangGraph Platform" has been renamed to **"LangSmith Deployment"**. This affects documentation and product naming, but APIs remain the same.

### Core Requirements:
- **NEVER ADD A CHECKPOINTER** unless explicitly requested by user
- Always export compiled graph as `app`
- Use prebuilt components when possible
- Follow model preference hierarchy: Anthropic > OpenAI > Google
- Keep state minimal (MessagesState usually sufficient)

#### AVOID unless user specifically requests
```python
# Don't do this unless asked!
from langgraph.checkpoint.memory import MemorySaver
graph = create_react_agent(model, tools, checkpointer=MemorySaver())
```

#### For existing codebases
- Always search for existing graph export patterns first
- Work within the established structure rather than imposing new patterns
- Do not create `agent.py` if graphs are already exported elsewhere

### Standard Structure for New Projects:
```
./agent.py          # Main agent file, exports: app
./langgraph.json    # LangGraph configuration
```

### Export Pattern:
```python
from langgraph.graph import StateGraph, START, END
# ... your state and node definitions ...

# Build your graph
graph_builder = StateGraph(YourState)
# ... add nodes and edges ...

# Export as 'app' for new agents from scratch
graph = graph_builder.compile()
app = graph  # Required for new LangGraph agents
```

## Prefer Prebuilt Components

**Always use prebuilt components when possible** - they are deployment-ready and well-tested.

### Basic Agents - Use create_agent (LangChain 1.0):
```python
from langchain.agents import create_agent

# Simple, deployment-ready agent (NEW in LangChain 1.0)
agent = create_agent(
    model="anthropic:claude-sonnet-4-5",  # Can use string or BaseChatModel
    tools=tools,
    system_prompt="Your agent instructions here"
)
app = agent

# With checkpointer and store (optional)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    system_prompt="You are a helpful assistant",
    checkpointer=MemorySaver(),  # Only if explicitly needed
    store=InMemoryStore()         # For long-term memory
)
app = agent
```

**Migration Note**: The old `create_react_agent` from `langgraph.prebuilt` is deprecated:
```python
# OLD (Deprecated in LangGraph 1.0):
from langgraph.prebuilt import create_react_agent

# NEW (Use this instead):
from langchain.agents import create_agent
```

### Multi-Agent Systems:

#### Supervisor Pattern (central coordination):
```python
from langgraph_supervisor import create_supervisor

supervisor = create_supervisor(
    agents=[agent1, agent2],
    model=model,
    prompt="You coordinate between agents..."
)
app = supervisor.compile()
```
Documentation: https://langchain-ai.github.io/langgraph/reference/supervisor/

#### Swarm Pattern (dynamic handoffs):
```python
from langgraph_swarm import create_swarm, create_handoff_tool

alice = create_react_agent(
    model,
    [tools, create_handoff_tool(agent_name="Bob")],
    prompt="You are Alice.",
    name="Alice",
)

workflow = create_swarm([alice, bob], default_active_agent="Alice")
app = workflow.compile()
```
Documentation: https://langchain-ai.github.io/langgraph/reference/swarm/

#### Deep Agents Pattern (complex, multi-step tasks):
```python
from deepagents import create_deep_agent

# Create a deep agent with planning, sub-agents, and file system
# NEW: Deep Agents now use the middleware architecture
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    system_prompt="You are a research assistant capable of deep investigation...",
    # Deep agents automatically include:
    # - PlanningMiddleware (write_todos tool)
    # - FilesystemMiddleware (ls, read_file, write_file, edit_file, glob, grep)
    # - SubAgentMiddleware (task tool for spawning sub-agents)
)
app = agent

# Can customize with additional middleware
from langchain.agents.middleware import SummarizationMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    middleware=[SummarizationMiddleware(max_messages=30)]  # Add to default middleware
)
```
Documentation: https://docs.langchain.com/labs/deep-agents/overview

**What makes Deep Agents different:**
- **Planning Tool**: Built-in `write_todos` tool via TodoListMiddleware enables agents to break down complex tasks
- **File System Access**: Agents can offload large context to files via FilesystemMiddleware
- **Sub-Agents**: Built-in `task` tool via SubAgentMiddleware enables spawning specialized sub-agents
- **Detailed System Prompts**: Heavily inspired by Claude Code, includes extensive instructions and few-shot examples
- **Long-Term Memory**: Extend with LangGraph's Store for persistent memory across threads
- **Built on Middleware**: Deep Agents use LangChain 1.0's middleware architecture for composability

**When to use Deep Agents:**
- Complex research tasks requiring multi-step planning
- Long-running tasks that need context management
- Tasks requiring specialized sub-agents for different aspects
- Applications needing to manage large amounts of context
- Coding agents or deep research assistants

### Only Build Custom StateGraph When:
- Prebuilt components don't fit the specific use case
- User explicitly asks for custom workflow
- Complex branching logic required
- Advanced streaming patterns needed

## Model Preferences

**LLM MODEL PRIORITY** (follow this order):
```python
# 1. PREFER: Anthropic
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# 2. SECOND CHOICE: OpenAI 
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o")

# 3. THIRD CHOICE: Google
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
```

**NOTE**: Assume API keys are available in environment.
During development, ignore missing key errors.

## Middleware System (NEW in LangChain 1.0)

**Middleware** is LangChain 1.0's solution for fine-grained control over agent execution. It provides hooks to intercept and modify the agent loop at key points.

### Why Middleware?
Traditional agents lack control over **context engineering** - what goes into the model determines what comes out. Middleware gives you surgical control over the agent loop without building from scratch.

### Three Core Hooks:

#### 1. `before_model` - Runs before LLM invocation
```python
from langchain.agents.middleware import AgentMiddleware

class LoggingMiddleware(AgentMiddleware):
    async def before_model(self, state, config):
        print(f"About to call model with {len(state['messages'])} messages")
        return state  # Can modify state here
```

#### 2. `after_model` - Runs after LLM response
```python
class ValidationMiddleware(AgentMiddleware):
    async def after_model(self, state, config):
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls'):
            # Validate tool calls before execution
            validated_calls = self.validate_tool_calls(last_message.tool_calls)
            # Can modify or reject tool calls
        return state
```

#### 3. `modify_model_request` - Modify the request before LLM call
```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def dynamic_model_middleware(model_request, config):
    # Change model based on task complexity
    if is_complex_task(model_request.messages):
        model_request.model = "anthropic:claude-opus-4"
    
    # Add/modify tools dynamically
    model_request.tools.append(additional_tool)
    
    # Modify system prompt
    model_request.system_prompt = f"Enhanced: {model_request.system_prompt}"
    
    return model_request
```

### Execution Order:
Middleware runs sequentially like web server middleware:
```
Request Flow:
User Input 
  → Middleware 1: before_model
  → Middleware 2: before_model
  → Middleware 3: before_model
  → All: modify_model_request
  → LLM Call
  ← Middleware 3: after_model
  ← Middleware 2: after_model
  ← Middleware 1: after_model
  ← Final Response
```

### Built-in Middleware:

#### HumanInTheLoopMiddleware - Pause for human approval
```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[risky_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            tools_requiring_approval=["process_refund", "delete_data"]
        )
    ],
    checkpointer=MemorySaver()  # Required for HITL
)
```

#### SummarizationMiddleware - Manage context window
```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    middleware=[
        SummarizationMiddleware(
            max_messages=20,  # Summarize when messages exceed this
            summarization_model="openai:gpt-4o-mini"
        )
    ]
)
```

#### TodoListMiddleware - Planning for complex tasks
```python
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    middleware=[
        TodoListMiddleware(
            system_prompt_addition="Break complex tasks into steps using write_todos"
        )
    ]
)
# Agent now has access to write_todos tool for planning
```

### Using Multiple Middleware:
```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    SummarizationMiddleware,
    HumanInTheLoopMiddleware,
    TodoListMiddleware
)

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    middleware=[
        SummarizationMiddleware(max_messages=20),
        TodoListMiddleware(),
        HumanInTheLoopMiddleware(tools_requiring_approval=["risky_tool"])
    ],
    checkpointer=MemorySaver()
)
```

### Custom Middleware Example:
```python
from langchain.agents.middleware import AgentMiddleware

class CustomMetricsMiddleware(AgentMiddleware):
    """Track custom metrics during agent execution"""
    
    async def before_model(self, state, config):
        self.start_time = time.time()
        return state
    
    async def after_model(self, state, config):
        duration = time.time() - self.start_time
        logger.info(f"Model call took {duration}s")
        return state
    
    async def modify_model_request(self, model_request, config):
        # Add custom metadata
        model_request.metadata["user_id"] = config.get("user_id")
        return model_request

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=tools,
    middleware=[CustomMetricsMiddleware()]
)
```

### When to Use Middleware:
- **Context Window Management**: Auto-summarize long conversations
- **Human Oversight**: Require approval for sensitive operations
- **Task Planning**: Add structured planning capabilities
- **Dynamic Routing**: Select models/tools based on context
- **Logging & Monitoring**: Track agent behavior and performance
- **Security**: Validate/filter tool calls or inputs
- **Cost Optimization**: Route to cheaper models when appropriate

### Middleware vs Custom StateGraph:
- **Use Middleware**: When you need to modify behavior of standard agent loop
- **Use Custom StateGraph**: When you need completely different control flow

Documentation: https://docs.langchain.com/oss/python/langchain/agents#middleware

## Message and State Handling

### CRITICAL: Extract Message Content Properly
```python
# CORRECT: Extract message content properly
result = agent.invoke({"messages": state["messages"]})
if result.get("messages"):
    final_message = result["messages"][-1]  # This is a message object
    content = final_message.content         # This is the string content

# WRONG: Treating message objects as strings
content = result["messages"][-1]  # This is an object, not a string!
if content.startswith("Error"):   # Will fail - objects don't have startswith()
```

### State Updates Must Be Dictionaries:
```python
def my_node(state: State) -> Dict[str, Any]:
    # Do work...
    return {
        "field_name": extracted_string,    # Always return dict updates
        "messages": updated_message_list   # Not the raw messages
    }
```

## Memory and State Management

LangGraph provides two types of memory for building sophisticated agents:

### Short-Term Memory (Thread-Level Persistence)
Use checkpointers for conversation continuity within a single thread/session.

```python
from langgraph.checkpoint.memory import InMemorySaver

# For development
checkpointer = InMemorySaver()

# For production - use persistent storage
from langgraph.checkpoint.postgres import PostgresSaver
DB_URI = "postgresql://user:pass@localhost:5432/db"
checkpointer = PostgresSaver.from_conn_string(DB_URI)

# Compile graph with checkpointer
graph = builder.compile(checkpointer=checkpointer)

# Use with thread_id to maintain conversation history
graph.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    {"configurable": {"thread_id": "conversation-1"}}
)
```

### Long-Term Memory (Cross-Thread Persistence)
Use LangGraph Store for memory that persists across multiple conversation sessions.

```python
from langgraph.store.memory import InMemoryStore

# For development
store = InMemoryStore()

# For production - use database-backed store
from langgraph_checkpoint_postgres import PostgresStore
store = PostgresStore(DB_URI)

# Store user preferences across threads
user_id = "user_123"
namespace = (user_id, "preferences")
store.put(namespace, "food", {"preference": "vegetarian"})

# Retrieve memories
memories = store.search(namespace)
memory = store.get(namespace, "food")

# Use store in agent nodes
def my_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "memories")
    
    # Search for relevant memories
    memories = store.search(namespace)
    
    # Use memories in your logic
    # ...
    
    # Store new memories
    store.put(namespace, memory_id, {"content": "user likes AI"})
    
    return {"messages": [response]}

# Compile with store
graph = builder.compile(checkpointer=checkpointer, store=store)
```

### Memory Patterns:
- **InMemoryStore**: For development/testing (data lost on restart)
- **PostgresStore**: For production (persistent across restarts)
- **RedisStore**: For high-performance applications
- **MongoDBStore**: For flexible JSON document storage with vector search

### When to Use Each:
- **Short-term memory (checkpointer)**: Multi-turn conversations, maintaining context within a session
- **Long-term memory (store)**: User preferences, learned behaviors, cross-session knowledge
- **Both together**: Most production agents benefit from using both for complete memory support

Documentation:
- Memory Overview: https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/
- Long-Term Memory: https://blog.langchain.com/launching-long-term-memory-support-in-langgraph/
- Store API: https://langchain-ai.github.io/langgraph/concepts/persistence/

## Streaming and Interrupts

### Streaming Patterns:
- Interrupts only work with `stream_mode="updates"`, not `stream_mode="values"`
- In "updates" mode, events are structured as `{node_name: node_data, ...}`
- Check for `"__interrupt__"` key directly in the event object
- Iterate through `event.items()` to access individual node outputs

- Interrupts appear as `event["__interrupt__"]` containing a tuple of `Interrupt` objects
- Access interrupt data via `interrupt_obj.value` where `interrupt_obj = event["__interrupt__"][0]`

Documentation:
- LangGraph Streaming: https://langchain-ai.github.io/langgraph/how-tos/stream-updates/
- SDK Streaming: https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/#stream
- Concurrent Interrupts: https://docs.langchain.com/langgraph-platform/interrupt-concurrent

### When to Use Interrupts:
Use `interrupt()` when you need:
- User approval for generated plans or proposed changes
- Human confirmation before executing potentially risky operations
- Additional clarification when the task is ambiguous
- User input data entry or for decision points that require human judgment
- Feedback on partially completed work before proceeding

### Correct Interrupt Usage:
```python
# CORRECT: interrupt() pauses execution for human input
interrupt("Please confirm action")
# Execution resumes after human provides input through platform

# AVOID: Treating interrupt() as synchronous
result = interrupt("Please confirm action")  # Wrong - doesn't return values
if result == "yes":  # This won't work
    proceed()
```

## Deep Research Agent Pattern

**Deep Research** is a sophisticated pattern for building agents that can autonomously conduct multi-step research, similar to OpenAI's Deep Research, Google's Gemini Deep Research, or Claude's research features.

### Key Components:
1. **Query Planning**: Break down vague research questions into structured research plans
2. **Iterative Search**: Continuously search and evaluate if enough information has been gathered
3. **Source Evaluation**: Assess quality and relevance of search results
4. **Synthesis**: Generate comprehensive reports with proper citations
5. **Adaptive Behavior**: Circle back for more searches when information is insufficient

### Implementation Patterns:
```python
from deepagents import create_deep_agent
from langgraph.graph import StateGraph

# Option 1: Using Deep Agents (simpler)
agent = create_deep_agent(
    model=model,
    tools=[web_search_tool, web_scraper_tool],
    prompt="""You are a research assistant. Given a query:
    1. Plan your research approach using write_todos
    2. Search systematically for information
    3. Evaluate if you have enough information
    4. Synthesize findings into a comprehensive report
    """
)

# Option 2: Custom StateGraph (more control)
class ResearchState(TypedDict):
    query: str
    search_results: List[Dict]
    report: str
    iterations: int
    sufficient_info: bool

def plan_research(state: ResearchState):
    # Generate research plan
    pass

def search_web(state: ResearchState):
    # Execute web searches
    pass

def evaluate_results(state: ResearchState):
    # Determine if enough information gathered
    pass

def should_continue_research(state: ResearchState):
    if state["sufficient_info"] or state["iterations"] >= 5:
        return "synthesize"
    return "search"

builder = StateGraph(ResearchState)
builder.add_node("plan", plan_research)
builder.add_node("search", search_web)
builder.add_node("evaluate", evaluate_results)
builder.add_conditional_edges("evaluate", should_continue_research)
```

### Best Practices:
- Use search APIs optimized for AI (e.g., Tavily, Exa) rather than standard search
- Implement web scraping for full article content (e.g., Crawl4AI, Firecrawl)
- Use reranking models (e.g., Cohere) to identify most relevant content
- Store intermediate findings in files for context management
- Implement proper citation tracking throughout the research process
- Set maximum iteration limits to prevent infinite loops
- Use sub-agents for specialized research subtopics

### Reference Implementations:
- Google's Open Deep Research: https://github.com/langchain-ai/open_deep_research
- Deep Research with MCP: Various community implementations on GitHub

Documentation: https://blog.langchain.com/deep-agents/

## Common LangGraph Errors to Avoid

- Incorrect `interrupt()` usage: It pauses execution, doesn't return values
- Refer to documentation for best interrupt handling practices, including waiting for user input and proper handling of it
- Wrong state update patterns: Return updates, not full state
- Missing state type annotations
- Missing state fields (current_field, user_input)
- Invalid edge conditions: Ensure all paths have valid transitions
- Not handling error states properly
- Not exporting graph as 'app' when creating new LangGraph agents from scratch
- Forgetting `langgraph.json` configuration
- **Type assumption errors**: Assuming message objects are strings, or that state fields are certain types
- **Chain operations without type checking**: Like `state.get("field", "")[-1].method()` without verifying types
- **Using checkpointer when not needed**: Only add checkpointers when explicitly requested for deployment
- **Confusing Store vs Checkpointer**: Use checkpointers for short-term (thread-level) memory, Store for long-term (cross-thread) memory
- **Not using prebuilt agents**: Using custom StateGraph when `create_agent` or `create_deep_agent` would suffice
- **Using deprecated APIs**: Don't use `langgraph.prebuilt.create_react_agent`, use `langchain.agents.create_agent` instead (as of LangChain 1.0)

## Framework Integration Patterns

### Model Context Protocol (MCP) Integration

**MCP** is an open protocol that standardizes how AI applications connect to external data sources and tools. LangGraph has native support for MCP, allowing agents to auto-discover and use tools that follow this standard.

#### Using MCP with LangGraph:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async def mcp_tools_node(state, config):
    # Connect to MCP servers
    client = MultiServerMCPClient({
        "github": {
            "transport": "streamable_http",
            "url": "https://my-mcp-server/mcp",
            "headers": {"Authorization": f"Bearer {token}"}
        },
        "filesystem": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "mcp_server_filesystem"]
        }
    })
    
    # Get all available tools from MCP servers
    tools = await client.get_tools()
    
    # Use tools in your agent
    # ... tool calling logic
    
    return {"messages": tool_messages}
```

#### Key Benefits:
- **Standardized Tool Discovery**: Agents can automatically discover available tools from MCP servers
- **Multi-Server Support**: Connect to multiple MCP servers simultaneously
- **Tool Interoperability**: Works with hundreds of existing MCP tool servers
- **Native Integration**: LangGraph Platform has built-in MCP endpoint support

#### MCP Transports:
- **streamable_http**: HTTP-based transport for remote servers
- **stdio**: Standard input/output for local processes
- **sse**: Server-sent events for streaming

#### LangGraph Server MCP Endpoint:
When deploying with LangGraph Platform, your agents automatically expose an MCP endpoint at `/mcp`, making them accessible as tools to other MCP clients.

Documentation:
- MCP Integration: https://docs.langchain.com/langgraph-platform/server-mcp
- LangChain MCP Adapters: https://changelog.langchain.com/announcements/mcp-adapters-for-langchain-and-langgraph

## Framework Integration Patterns

### Integration Debugging
When building integrations, always start with debugging:

```python
# Temporary debugging for new integrations
def my_integration_function(input_data, config):
    print(f"=== DEBUG START ===")
    print(f"Input type: {type(input_data)}")
    print(f"Input data: {input_data}")
    print(f"Config type: {type(config)}")
    print(f"Config data: {config}")
    
    # Process...
    result = process(input_data, config)
    
    print(f"Result type: {type(result)}")
    print(f"Result data: {result}")
    print(f"=== DEBUG END ===")
    
    return result
```

### Config Propagation Verification
Always verify the receiving end actually uses configuration:

```python
# WRONG: Assuming config is used
def my_node(state: State) -> Dict[str, Any]:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# CORRECT: Actually using config
def my_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    # Extract configuration
    configurable = config.get("configurable", {})
    system_prompt = configurable.get("system_prompt", "Default prompt")
    
    # Use configuration in messages
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}
```
## Patterns to Avoid

### Don't Mix Responsibilities in Single Nodes:
```python
# AVOID: LLM call + tool execution in same node
def bad_node(state):
    ai_response = model.invoke(state["messages"])  # LLM call
    tool_result = tool_node.invoke({"messages": [ai_response]})  # Tool execution
    return {"messages": [...]}  # Mixed concerns!

# PREFER: Separate nodes for separate concerns
def llm_node(state):
    return {"messages": [model.invoke(state["messages"])]}

def tool_node(state):
    return ToolNode(tools).invoke(state)

# Connect with edges
workflow.add_edge("llm", "tools")
```

### Overly Complex Agents When Simple Ones Suffice
```python
# AVOID: Unnecessary complexity
workflow = StateGraph(ComplexState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
# ... 20 lines of manual setup when create_react_agent would work
```

### Avoid Overly Complex State:
```python
# AVOID: Too many state fields
class State(TypedDict):
    messages: List[BaseMessage]
    user_input: str
    current_step: int
    metadata: Dict[str, Any]
    history: List[Dict]
    # ... many more fields

# PREFER: Use MessagesState when sufficient
from langgraph.graph import MessagesState
```

### Wrong Export Patterns
```python
# AVOID: Wrong variable names or missing export
compiled_graph = workflow.compile()  # Wrong name
# Missing: app = compiled_graph
```

### Incorrect interrupt() usage
```python
# AVOID: Treating interrupt() as synchronous
result = interrupt("Please confirm action")  # Wrong - doesn't return values
if result == "yes":  # This won't work
    proceed()

# CORRECT: interrupt() pauses execution for human input
interrupt("Please confirm action")
# Execution resumes after human provides input through platform
```
Reference: https://langchain-ai.github.io/langgraph/concepts/streaming/#whats-possible-with-langgraph-streaming

## LangGraph-Specific Coding Standards

### Structured LLM Calls and Validation
When working with LangGraph nodes that involve LLM calls, always use structured output with Pydantic dataclasses:

- Use `with_structured_output()` method for LLM calls that need specific response formats
- Define Pydantic BaseModel classes for all structured data (state schemas, LLM responses, tool inputs/outputs)
- Validate and parse LLM responses using Pydantic models
- For conditional nodes relying on LLM decisions, use structured output

Example: `llm.with_structured_output(MyPydanticModel).invoke(messages)` instead of raw string parsing

### General Guidelines:
- Test small components before building complex graphs
- **Avoid unnecessary complexity**: Consider if simpler approaches with prebuilt components would achieve the same goals
- Write concise and clear code without overly verbose implementations
- Only install trusted, well-maintained packages

### Package Installation:
```bash
# LangChain 1.0 & LangGraph 1.0 (October 2025)
pip install --upgrade langchain langgraph

# For legacy LangChain v0.x functionality
pip install langchain-classic

# Model providers (no --pre flag needed)
pip install langchain-openai langchain-anthropic langchain-google-genai

# Deep Agents
pip install deepagents

# MCP Adapters
pip install langchain-mcp-adapters

# Memory/Store backends (choose based on needs)
pip install langgraph-checkpoint-postgres  # PostgreSQL checkpointer and store
pip install langgraph-checkpoint-redis     # Redis checkpointer and store
pip install langgraph-store-mongodb        # MongoDB store

# Using uv (faster alternative)
uv pip install --upgrade langchain langgraph
uv add langchain langchain-openai
```

**Python Version**: LangChain 1.0 requires Python 3.10 or later (Python 3.9 support dropped as of October 2025)

## Documentation Guidelines

### When to Consult Documentation:
Always use documentation tools before implementing LangGraph code (the API evolves rapidly):
- Before creating new graph nodes or modifying existing ones
- When implementing state schemas or message passing patterns
- Before using LangGraph-specific decorators, annotations, or utilities
- When working with conditional edges, dynamic routing, or subgraphs
- Before implementing tool calling patterns within graph nodes
- When building applications that integrate multiple frameworks (e.g., LangGraph + Streamlit, LangGraph + Next.js/React), also consult the framework docs to ensure correct syntax and patterns

### NEW: Unified Documentation Site (October 2025)
As of LangChain/LangGraph 1.0, all documentation is now unified at **https://docs.langchain.com**:
- Python and JavaScript docs side-by-side
- Shared conceptual guides
- Consolidated API references
- Easier navigation across LangChain and LangGraph

### Key Documentation Resources:
- **Main Docs**: https://docs.langchain.com
- LangGraph Overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangChain Agents (create_agent): https://docs.langchain.com/oss/python/langchain/agents
- Middleware: https://docs.langchain.com/oss/python/langchain/agents#middleware
- LangGraph Streaming: https://langchain-ai.github.io/langgraph/how-tos/stream-updates/
- LangGraph Config: https://langchain-ai.github.io/langgraph/how-tos/pass-config-to-tools/
- Supervisor Pattern: https://langchain-ai.github.io/langgraph/reference/supervisor/
- Swarm Pattern: https://langchain-ai.github.io/langgraph/reference/swarm/
- Deep Agents: https://docs.langchain.com/labs/deep-agents/overview
- Agentic Concepts: https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/
- Memory Management: https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/
- MCP Integration: https://docs.langchain.com/langgraph-platform/server-mcp
- Store API (Long-term Memory): https://langchain-ai.github.io/langgraph/concepts/persistence/
- LangGraph 1.0 Blog: https://blog.langchain.com/langchain-langgraph-1dot0/

### Documentation Navigation
- Determine the base URL from the current documentation page
- For `../`, go one level up in the URL hierarchy
- For `../../`, go two levels up, then append the relative path
- Example: From `https://langchain-ai.github.io/langgraph/tutorials/get-started/langgraph-platform/setup/` with link `../../langgraph-platform/local-server`
  - Go up two levels: `https://langchain-ai.github.io/langgraph/tutorials/get-started/`
  - Append path: `https://langchain-ai.github.io/langgraph/tutorials/get-started/langgraph-platform/local-server`
- If you encounter an HTTP 404 error, the constructed URL is likely incorrect—rebuild it carefully