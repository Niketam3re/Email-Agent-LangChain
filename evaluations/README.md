# Email AI Agent - Evaluation Suite

Complete evaluation infrastructure using LangSmith for testing and improving your agent before production deployment.

## 📁 What's Included

```
evaluations/
├── README.md (this file)
├── sample_emails_for_langsmith.py   # Generate 300 mock emails
├── create_dataset.py                # Upload to LangSmith
├── evaluate_agent.py                # Run evaluations
├── import_my_emails.py              # Import your own emails
└── evaluators/
    ├── __init__.py
    ├── category_accuracy.py         # Category matching evaluator
    ├── response_quality.py          # Response quality evaluator
    └── pattern_detection.py         # Pattern detection evaluator
```

## 🚀 Quick Start (3 Commands)

```bash
# 1. Generate sample emails (300 diverse examples)
python sample_emails_for_langsmith.py

# 2. Upload to LangSmith
python create_dataset.py

# 3. Run evaluation
python evaluate_agent.py
```

## 📊 What Gets Evaluated

### Metrics:
- **Category Accuracy** (target: >0.85)
  - Exact match: 1.0
  - Parent category correct: 0.7
  - No match: 0.0

- **Tone Match** (target: >0.80)
  - Correct tone detection
  - Handles synonyms (formal = professional)

- **Formality Match** (target: >0.75)
  - High/Medium/Low formality
  - Partial credit for close levels

- **Confidence Calibration** (target: >0.70)
  - High confidence + correct = good
  - High confidence + incorrect = overconfident (bad)
  - Low confidence + incorrect = acceptable

- **Internal Consistency** (target: >0.85)
  - Category matches tone/formality
  - E.g., Work → professional tone → high formality

## 📧 Sample Dataset

300 emails across:
- **Work** (120): Project Alpha (40), Project Beta (40), Meetings (40)
- **Hockey** (60): Team A (30), Team B (30)
- **Personal** (50): Family (25), Friends (25)
- **Finance** (30)
- **Shopping** (30)
- **Organizational** (30)
- **Travel** (20)

Each email includes:
- Inputs: from, subject, body, date
- Expected: category, tone, formality, response_length

## 🔄 Iteration Workflow

```
Generate Samples → Upload → Evaluate → Analyze in LangSmith UI
                                ↓
                    Update System Prompt
                                ↓
                    Re-evaluate & Compare ← ← ← ←
```

## 📈 Viewing Results

After running evaluation:

1. Go to https://smith.langchain.com/
2. Select project: `email-ai-agent`
3. Click "Datasets" tab
4. View evaluation run

**You'll see:**
- 📊 Overall metrics dashboard
- 📧 Individual email pass/fail
- 🔍 Full traces for debugging
- ⚠️  Failed cases highlighted
- 📈 Charts by category

## 🎯 Success Criteria

Ready for production when:
- ✅ Category Accuracy > 0.85
- ✅ Tone Match > 0.80
- ✅ Formality Match > 0.75
- ✅ Confidence Calibration > 0.70
- ✅ Internal Consistency > 0.85
- ✅ No systematic failures

## 📚 Full Documentation

See `../EVALUATION_GUIDE.md` for:
- Complete workflow details
- Metric explanations
- Failure pattern analysis
- Iteration strategies
- Adding your own emails
- Custom evaluator creation

## 🆘 Troubleshooting

### "Dataset not found"
```bash
python create_dataset.py  # Create dataset first
```

### "LANGSMITH_API_KEY not found"
Add to `.env`:
```bash
LANGSMITH_API_KEY=lsv2_pt_xxxxx
LANGSMITH_TRACING=true
```

### "Taking too long"
Edit `evaluate_agent.py`:
```python
max_concurrency=2  # Reduce from 5
```

### View a sample email
```bash
python -c "
import json
with open('sample_emails_dataset.json') as f:
    emails = json.load(f)
    print(json.dumps(emails[0], indent=2))
"
```

## 💡 Pro Tips

1. **Start with generated samples** - faster iteration
2. **Add your real emails** once agent is working well
3. **Compare runs** in LangSmith UI to track progress
4. **Focus on failed cases** - most learning happens here
5. **Update prompt systematically** - one change at a time
6. **Set confidence thresholds** for auto vs manual review

## 🎓 Next Steps

1. ✅ Generate and review sample emails
2. ✅ Upload to LangSmith
3. ✅ Run initial evaluation
4. ✅ Analyze results
5. ✅ Iterate on system prompt
6. ✅ Re-evaluate and compare
7. ✅ Reach target metrics
8. ✅ Switch to production Gmail API

---

**Build confidence through evaluation before production! 🚀**
