# Email AI Agent - Quick Start Guide 🚀

Get up and running in 5 minutes!

## ⚡ Super Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your credentials (see below)

# 3. Run setup verification
python setup.py

# 4. Set up Supabase database
# Copy contents of supabase/schema.sql into Supabase SQL Editor and run

# 5. Test the agent
python example_usage.py
```

## 🔑 Required Credentials

Add these to your `.env` file:

### 1. Anthropic API Key
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```
Get it from: https://console.anthropic.com/

### 2. Supabase
```bash
SUPABASE_OAUTH_TOKEN=sbp_xxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
```
- Create project at: https://app.supabase.com/
- Get OAuth token from: https://supabase.com/dashboard/account/tokens
- Run `supabase/schema.sql` in SQL Editor

### 3. Gmail MCP (Default setup)
```bash
GMAIL_MCP_COMMAND=uvx
GMAIL_MCP_ARGS=mcp-server-gmail
```
- Install uvx: `pip install uvx`
- Or use alternative Gmail MCP server (see README)

### 4. LangSmith (Optional but recommended)
```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_xxxxx
LANGSMITH_PROJECT=email-ai-agent
```
Get it from: https://smith.langchain.com/

## 📝 First Run

### Option A: Interactive Examples
```bash
python example_usage.py
```
Select option 1 for initial inbox scan.

### Option B: Direct Python
```python
import asyncio
from agent import create_email_agent

async def scan():
    agent = await create_email_agent()
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Scan my inbox and create categories"}]
    })
    print(result["messages"][-1].content)

asyncio.run(scan())
```

### Option C: LangGraph Server
```bash
# Install LangGraph CLI
pip install langgraph-cli

# Start development server
langgraph dev

# Access at http://localhost:8123
```

## 🎯 What Happens on First Run

1. **Agent connects** to Gmail via MCP
2. **Scans emails** (all or last N)
3. **Identifies categories** (Work, Personal, Hockey, etc.)
4. **Classifies emails** into categories
5. **Analyzes patterns** (tone, formality, length)
6. **Generates rules** for drafting responses
7. **Creates diagram** showing inbox structure
8. **Stores everything** in Supabase

## 🔍 Verify Setup

```bash
# Run automated checks
python setup.py

# Should show all ✅ checks passing
```

## 🐛 Common Issues

### "No module named 'deepagents'"
```bash
pip install deepagents
```

### "Gmail MCP server not found"
```bash
pip install uvx
uvx --help  # Verify it works
```

### "Supabase connection failed"
- Check SUPABASE_OAUTH_TOKEN starts with `sbp_`
- Verify SUPABASE_URL format: `https://xxx.supabase.co`
- Run schema.sql in Supabase SQL Editor

### "Anthropic API error"
- Verify API key starts with `sk-ant-`
- Check account has credits: https://console.anthropic.com/

## 📊 View Results

### LangSmith (Recommended)
1. Go to https://smith.langchain.com/
2. Select your project (`email-ai-agent`)
3. View detailed traces of all operations

### Supabase
1. Go to https://app.supabase.com/
2. Open your project
3. View `email_categories`, `communication_patterns`, `response_rules` tables

## 🎓 Next Steps

1. ✅ Run initial inbox scan
2. ✅ Review identified categories in Supabase
3. ✅ Test draft response generation
4. ✅ Check LangSmith traces
5. ✅ Customize system prompt in `agent.py`
6. ✅ Deploy with `langgraph deploy`

## 💡 Pro Tips

- **Start small**: Test with last 100 emails first
- **Use LangSmith**: Essential for debugging
- **Check traces**: See exactly what the agent is doing
- **Iterate on rules**: Update response rules based on feedback
- **Monitor costs**: Claude API calls add up

## 📚 Full Documentation

See `README.md` for:
- Complete setup instructions
- Architecture details
- Advanced usage
- Security best practices
- Troubleshooting guide

## 🆘 Need Help?

1. Run `python setup.py` to diagnose issues
2. Check logs in LangSmith
3. Review README.md troubleshooting section
4. Check LangGraph docs: https://docs.langchain.com/langgraph

---

**Ready to go? Run `python example_usage.py` and select option 1!** 🚀
