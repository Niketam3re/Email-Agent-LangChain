# Email AI Agent - Evaluation Guide 📊

Complete guide to evaluating and improving your email agent using LangSmith.

## 🎯 Why Evaluate?

Before connecting to real Gmail data, you want to:
1. **Test agent behavior** on controlled examples
2. **Measure accuracy** on known correct answers
3. **Identify weaknesses** in categorization and pattern detection
4. **Iterate quickly** without API rate limits
5. **Build confidence** before production deployment

## 📋 Evaluation Workflow

```
1. Generate Sample Emails
   ↓
2. Create LangSmith Dataset
   ↓
3. Run Evaluation
   ↓
4. Analyze Results in LangSmith UI
   ↓
5. Identify Issues & Update Prompt
   ↓
6. Re-run Evaluation & Compare
   ↓
7. Repeat until satisfied
   ↓
8. Deploy to production with Gmail
```

## 🚀 Quick Start

### Step 1: Generate Sample Emails

```bash
cd evaluations
python sample_emails_for_langsmith.py
```

This creates `sample_emails_dataset.json` with 300 diverse emails across:
- **Work** (120 emails): Project Alpha, Project Beta, Meetings
- **Hockey** (60 emails): Team A, Team B
- **Personal** (50 emails): Family, Friends
- **Finance** (30 emails)
- **Shopping** (30 emails)
- **Organizational** (30 emails)
- **Travel** (20 emails)

Each email includes:
- **Inputs**: `from`, `subject`, `body`, `date`, `has_attachments`
- **Expected outputs**: `category`, `tone`, `formality`, `response_length`

### Step 2: Upload Dataset to LangSmith

```bash
python create_dataset.py
```

This:
1. Connects to LangSmith API
2. Creates dataset named `email-agent-evaluation-v1`
3. Uploads all 300 email examples
4. Shows confirmation and dataset URL

**Output:**
```
✅ Created dataset with ID: abc-123
✅ Successfully uploaded 300 examples to LangSmith!

🔗 View dataset at: https://smith.langchain.com/datasets
   Dataset name: email-agent-evaluation-v1
```

### Step 3: Run Evaluation

```bash
python evaluate_agent.py
```

This:
1. Loads the dataset from LangSmith
2. Runs your agent on each email
3. Compares agent outputs to expected outputs
4. Calculates metrics using custom evaluators
5. Uploads results to LangSmith

**What's evaluated:**
- ✅ Category accuracy (exact match, partial match)
- ✅ Tone matching (formal, casual, friendly, urgent)
- ✅ Formality level (high, medium, low)
- ✅ Confidence calibration (appropriate confidence levels)
- ✅ Internal consistency (category matches tone/formality)

**Output:**
```
🚀 Starting evaluation...
   Max concurrency: 5
   This may take several minutes...

✅ Evaluation complete!

📊 Results Summary:
   category_accuracy: 0.87
   tone_match: 0.83
   formality_match: 0.79
   confidence_calibration: 0.75

🔗 View full results in LangSmith:
   https://smith.langchain.com/
```

### Step 4: Analyze in LangSmith UI

Go to https://smith.langchain.com/ and:

1. **Select your project** (`email-ai-agent`)
2. **Click on "Datasets"** tab
3. **View the evaluation run**
4. **See overall metrics** dashboard

**What you'll see:**
- 📊 **Aggregate metrics** across all emails
- 📈 **Charts** showing performance by category
- 📧 **Individual email results** with pass/fail
- 🔍 **Full traces** for each evaluation
- ⚠️  **Failed cases** highlighted

## 📊 Understanding Metrics

### 1. Category Accuracy (Most Important)
**What it measures:** Can the agent correctly identify which category an email belongs to?

**Scoring:**
- `1.0`: Exact match (e.g., "Work > Project Alpha")
- `0.7`: Parent category correct (got "Work" but missed "Project Alpha")
- `0.5`: Partial match (some overlap)
- `0.0`: Complete mismatch

**Target:** `> 0.85` (85% accuracy)

**If low:**
- Agent is confusing categories
- System prompt needs better category descriptions
- More examples needed for ambiguous categories

### 2. Tone Match
**What it measures:** Does the agent detect the correct tone (formal, casual, friendly, urgent)?

**Scoring:**
- `1.0`: Exact match or synonyms (e.g., "formal" = "professional")
- `0.7`: Related tones (e.g., "friendly" vs "warm")
- `0.0`: Unrelated tones

**Target:** `> 0.80`

**If low:**
- Agent is not picking up on tone cues
- System prompt needs tone examples
- Email samples may not have clear tone signals

### 3. Formality Match
**What it measures:** Does the agent detect the correct formality level (high, medium, low)?

**Scoring:**
- `1.0`: Exact match
- `0.5`: Off by one level (e.g., "medium" instead of "high")
- `0.0`: Off by two levels

**Target:** `> 0.75`

**If low:**
- Agent struggling to distinguish formality levels
- Add formality indicators to system prompt
- Provide more formality examples

### 4. Confidence Calibration
**What it measures:** Is the agent's confidence appropriately calibrated?

**Good calibration:**
- High confidence (>0.8) + Correct = ✅ Perfect
- Low confidence (<0.6) + Incorrect = ✅ Good (agent knew it was uncertain)
- High confidence (>0.8) + Incorrect = ❌ Overconfident (bad!)

**Target:** `> 0.70`

**If low:**
- Agent is overconfident on incorrect predictions
- Add uncertainty handling to system prompt
- Consider using temperature settings

### 5. Internal Consistency
**What it measures:** Are the agent's outputs internally consistent?

**Examples:**
- ✅ Good: "Work" category + "professional" tone + "high" formality
- ❌ Bad: "Work" category + "casual" tone + "low" formality

**Target:** `> 0.85`

**If low:**
- Agent's reasoning is inconsistent
- Add consistency requirements to system prompt
- Use structured output to enforce consistency

## 🔍 Analyzing Failed Cases

### In LangSmith UI:

1. **Filter by failed cases**
   - Click "Filters"
   - Select `category_accuracy < 0.5` or specific metric

2. **Review individual failures**
   - Click on a failed example
   - See full agent trace
   - Read agent's reasoning
   - Compare to expected output

3. **Identify patterns**
   - Are certain categories consistently wrong?
   - Do certain email types confuse the agent?
   - Is the agent missing key signals?

### Common Failure Patterns:

#### Pattern 1: Category Confusion
**Problem:** Agent confuses "Finance" and "Shopping" emails

**Solution:**
- Add clearer category descriptions to system prompt
- Add distinguishing examples to prompt
- Create subcategories if needed

**System Prompt Update:**
```python
"""
Categories:
- Finance: Bank statements, investment updates, bills (NOT shopping/orders)
- Shopping: Product orders, shipping, retail promotions (NOT financial statements)
"""
```

#### Pattern 2: Low Confidence on Correct Answers
**Problem:** Agent correct but not confident (confidence < 0.6)

**Solution:**
- Agent is being too cautious
- Add confidence guidelines to system prompt
- Review if examples are truly clear

#### Pattern 3: Overconfident on Incorrect Answers
**Problem:** Agent wrong but very confident (confidence > 0.8)

**Solution:**
- Add uncertainty language to system prompt
- Tell agent when to be uncertain
- Add edge case examples

#### Pattern 4: Tone Misdetection
**Problem:** Agent thinks formal emails are casual (or vice versa)

**Solution:**
- Add tone indicators to system prompt
- Provide tone examples
- List specific phrases that indicate tone

## 🔄 Iteration Process

### 1. Run Initial Evaluation
```bash
python evaluations/evaluate_agent.py
```

Note the run ID and overall metrics.

### 2. Identify Top Issues
Look for:
- Categories with lowest accuracy
- Most common confusion pairs
- Systematic errors

### 3. Update System Prompt
Edit `agent.py` system prompt based on findings.

**Example updates:**
```python
# Before
"Categorize this email into Work, Hockey, or Personal"

# After
"Categorize this email:
- Work: Professional emails from colleagues, projects, meetings
  - Look for: @company.com, project names, formal language
- Hockey: Team communications about practice, games, schedules
  - Look for: team names, 'practice', 'game', informal language
- Personal: Family and friends
  - Look for: personal email domains, casual tone, personal topics"
```

### 4. Re-run Evaluation
```bash
python evaluations/evaluate_agent.py
```

### 5. Compare in LangSmith
- Go to LangSmith UI
- Click "Compare" button
- Select your two evaluation runs
- See side-by-side metrics
- View which emails improved/worsened

### 6. Repeat Until Satisfied
Target metrics:
- Category Accuracy: **> 0.85**
- Tone Match: **> 0.80**
- Formality Match: **> 0.75**
- Confidence Calibration: **> 0.70**

## 📧 Adding Your Own Emails

### Option 1: JSON File

Create `my_emails.json`:
```json
[
  {
    "from": "boss@work.com",
    "subject": "Project status?",
    "body": "Hi, can you send me an update on the project?",
    "date": "2024-01-15 10:00:00",
    "expected_category": "Work > Project Alpha",
    "expected_tone": "professional",
    "expected_formality": "high"
  }
]
```

Import:
```bash
python evaluations/import_my_emails.py
# Select option 1 (JSON)
# Enter: my_emails.json
```

### Option 2: CSV File

Create `my_emails.csv`:
```csv
from,subject,body,date,expected_category,expected_tone,expected_formality
boss@work.com,Project status?,Can you send an update?,2024-01-15,Work > Project Alpha,professional,high
friend@gmail.com,Coffee?,Want to grab coffee?,2024-01-16,Personal > Friends,casual,low
```

Import:
```bash
python evaluations/import_my_emails.py
# Select option 2 (CSV)
# Enter: my_emails.csv
```

### Option 3: Python List

Edit `import_my_emails.py` `example_usage()` function:
```python
my_emails = [
    {
        "from": "...",
        "subject": "...",
        "body": "...",
        "expected_category": "...",
        # ...
    }
]
```

Run:
```bash
python evaluations/import_my_emails.py
# Select option 3
```

## 🔒 Privacy & Anonymization

The `import_my_emails.py` script includes anonymization features:

**Automatically anonymizes:**
- ✅ Email addresses → `user@example.com`
- ✅ Phone numbers → `xxx-xxx-xxxx`
- ✅ Account numbers → `xxxxxxxxxxxx`
- ✅ Dollar amounts → `$X,XXX`

**To use:**
```bash
python evaluations/import_my_emails.py
# When prompted: "Anonymize sensitive data? (y/n): y"
```

## 📈 Advanced: Custom Evaluators

You can create custom evaluators for specific use cases.

### Example: Check Draft Length

Create `evaluators/custom_length.py`:
```python
def draft_length_evaluator(run, example):
    expected_length = example.outputs.get("expected_response_length")
    draft = run.outputs.get("draft_response", "")

    word_count = len(draft.split())

    # Define length ranges
    if expected_length == "brief" and word_count <= 50:
        return {"key": "draft_length", "score": 1.0, "comment": "✅ Brief"}
    elif expected_length == "medium" and 50 < word_count <= 150:
        return {"key": "draft_length", "score": 1.0, "comment": "✅ Medium"}
    elif expected_length == "long" and word_count > 150:
        return {"key": "draft_length", "score": 1.0, "comment": "✅ Long"}
    else:
        return {"key": "draft_length", "score": 0.0, "comment": f"❌ Wrong length"}
```

Add to `evaluate_agent.py`:
```python
from evaluators.custom_length import draft_length_evaluator

results = evaluate(
    classify_and_analyze_email,
    data=dataset_name,
    evaluators=[
        category_accuracy_evaluator,
        tone_match_evaluator,
        formality_match_evaluator,
        confidence_threshold_evaluator,
        draft_length_evaluator  # Your custom evaluator
    ],
    # ...
)
```

## 🎓 Best Practices

### 1. Start with Good Samples
- Include edge cases
- Cover all categories evenly
- Include ambiguous emails
- Mix easy and hard examples

### 2. Set Realistic Targets
- Don't expect 100% accuracy
- Some emails are genuinely ambiguous
- 85-90% is excellent for most use cases

### 3. Iterate Systematically
- Change one thing at a time
- Always compare to previous run
- Document what changed
- Keep track of prompt versions

### 4. Use Confidence Thresholds
- Set minimum confidence for auto-categorization
- Flag low-confidence emails for manual review
- Track confidence distribution over time

### 5. Monitor Regression
- Keep a "golden" evaluation run
- Always compare new runs to golden
- Ensure new changes don't hurt existing performance

## 🚀 Moving to Production

Once evaluation metrics are good:

1. **✅ Category Accuracy > 0.85**
2. **✅ Tone Match > 0.80**
3. **✅ Formality Match > 0.75**
4. **✅ No systematic failures**

You're ready to:
1. Switch from mock emails to `agent.py` with real Gmail MCP
2. Run on small batch of real emails first (last 100)
3. Review results carefully
4. Gradually increase to full inbox
5. Continue monitoring in LangSmith

## 📚 Resources

- **LangSmith Docs**: https://docs.smith.langchain.com/
- **Evaluation Guide**: https://docs.smith.langchain.com/evaluation
- **LangGraph Docs**: https://docs.langchain.com/langgraph

## 🆘 Troubleshooting

### "Dataset not found"
```bash
# Run dataset creation first:
python evaluations/create_dataset.py
```

### "LANGSMITH_API_KEY not found"
```bash
# Add to .env file:
LANGSMITH_API_KEY=lsv2_pt_xxxxx
```

### "Evaluation taking too long"
```bash
# Reduce concurrency in evaluate_agent.py:
max_concurrency=2  # Default is 5
```

### "Agent errors on many emails"
- Check agent.py imports work
- Verify ANTHROPIC_API_KEY is set
- Test agent manually first

---

**Happy Evaluating! Build confidence before production deployment.** 🎉
