# Content Digest CLI — Research-to-Content Pipeline

> Scans Marcus/Galen research outputs, extracts tweet drafts and blog angles, compiles a daily digest for Seneca.

## Purpose

**Problem:** Seneca (coordinator) needs to quickly scan squad research outputs from Marcus and Galen without reading every full research file.

**Solution:** Content Digest CLI scans `~/.openclaw/learnings/` directory, extracts tweet drafts, blog angles, and signup links, compiles a daily digest for Seneca.

## Features

### Multi-Format Extraction
- **Tweet Drafts** — Extracts "Tweet Draft:" or "## Tweet Draft" sections from research files
- **Blog Angles** — Extracts "Blog Angle:" or "BLOG ANGLE:" sections
- **Signup Links** — Extracts "SIGNUP:" or "SIGNUP:" sections
- **Summaries** — Extracts executive summaries and key findings

### File Scanning
- Scans directory for markdown research files
- Filters out test files and the digest script itself
- Shows file age (days/hours/minutes ago)

### Output Formats
- **Markdown Digest** — Clean, formatted daily digest for Seneca
- **JSON Export** — Machine-readable format for further processing
- **Agent Grouping** — Groups content by agent (Marcus, Galen)

### Scan Command
- Scans directory for research files
- Reports count of research files found
- Skips non-research files

### Extract Command
- Extracts all actionable content from research files
- Organizes by agent
- Shows extraction summary (totals)

### Compile Command
- Creates formatted daily digest
- Includes tweet drafts, blog angles, signup links
- Adds summary section with totals

## Installation

```bash
# Clone or copy to your workspace
cd ~/.openclaw/workspace/tools/content-digest

# Create symlink for easy access
ln -s ~/.openclaw/workspace/tools/content-digest/content-digest.py ~/.local/bin/content-digest
chmod +x ~/.local/bin/content-digest

# Verify installation
content-digest --help
```

## Usage

### Scan Directory for Research Files

```bash
# Scan learnings directory
content-digest scan ~/.openclaw/learnings/
```

**Output:**
```
ℹ Found 12 research file(s) in ~/.openclaw/learnings/
```

---

### Extract Content for Digest

```bash
# Extract to JSON file
content-digest extract ~/.openclaw/learnings/ digest.json

# Extract to markdown file (default)
content-digest extract ~/.openclaw/learnings/
```

**Output:**
```
✓ Extracted: 5 tweet drafts, 8 blog angles, 2 signup links
```

---

### Compile Daily Digest

```bash
# Compile daily digest
content-digest compile ~/.openclaw/learnings/ daily-digest-2026-02-28.md

# Specify custom output file
content-digest compile ~/.openclaw/learnings/ output/summary.md
```

**Output:**
```
ℹ Compiled: /home/exedev/.openclaw/workspace/digest/daily-digest-2026-02-28.md
```

---

## Digest Format

### Markdown Digest Example

```markdown
# Squad Research Digest — February 28, 2026

Compiled by content-digest CLI
Source directory: `~/.openclaw/learnings/`

---

## 🐦 Tweet Drafts

### Marcus
- "ArXiv papers are getting better at math benchmarks. The new Claude Sonnet 3.5 model significantly outperforms GPT-4o on theorem-proving tasks." (1d ago, from marcus-ai-research-0228.md)
- "VAE models are showing remarkable progress in 3D structure generation. Could we build a comparative study across different architectures?" (2h ago, from marcus-ai-research-0229.md)

### Galen
- "CRISPR-Cas9 editing efficiency metrics show 45% reduction in off-target edits. This could revolutionize gene therapy workflows." (3h ago, from galen-biotech-research-045.md)

---

## ✍️ Blog Angles

### Marcus
- "The Math Model Hierarchy: Why Scaling Laws Still Matter" (1d ago, from marcus-ai-research-0228.md)
- "Zero-Shot vs Few-Shot: When to Use Which Approach?" (2h ago, from marcus-ai-research-0229.md)

### Galen
- "From Lab to Market: The CRISPR Timeline" (3h ago, from galen-biotech-research-045.md)
- "Gene Editing Safety: What We've Learned in 2025" (4h ago, from galen-biotech-research-046.md)

---

## 🔗 Signup Links

### Galen
- "GeneTherapy.com — Early access program" (2d ago, from galen-biotech-research-045.md)

---

## 📊 Summary

- Total files scanned: 12
- Tweet drafts: 5
- Blog angles: 8
- Signup links: 2
- Total actionable items: 15

Compiled: February 28, 2026 at 08:45 PM UTC
```

---

## Workflow Integration

### Cron Job Setup

```bash
# Add cron job for daily digest compilation
crontab -e

# Compile daily digest at 9:00 AM EST (2:00 PM UTC)
0 14 * * * content-digest compile ~/.openclaw/learnings/ ~/daily-digest-\$(date +\%Y\%m\%d).md

EOF
```

### Seneca Access

The daily digest file will be available at `~/daily-digest-YYYY-MM-DD.md`. Seneca can:
1. Read the file
2. Review tweet drafts for Twitter/X posting
3. Review blog angles for Run Data Run content
4. Track signup links for competitive intelligence

---

## Technical Details

### Extraction Patterns

**Tweet Drafts:**
- `Tweet Draft: <text>`
- `## Tweet Draft\n<text>`

**Blog Angles:**
- `Blog Angle: <text>`
- `BLOG ANGLE: <text>`

**Signup Links:**
- `SIGNUP: <text>`
- `SIGNUP: <text> <link>`

**Summaries:**
- `## Executive Summary`
- `## Key Findings`
- `## Summary`

### File Filtering

- Skips files starting with `content-digest` (to avoid self-scanning)
- Skips files starting with `test` (to avoid test files)
- Looks for research patterns to identify actual research files

### Agent Identification

Agent names are extracted from filenames:
- `marcus-ai-research-0228.md` → Agent: `marcus-ai-research`
- `galen-biotech-research-045.md` → Agent: `galen-biotech-research`

---

## Troubleshooting

### "No research files found" Error

**Cause:** Directory doesn't contain markdown files with research content.

**Solution:**
```bash
# Check directory contents
ls -la ~/.openclaw/learnings/

# Ensure files have research content patterns
grep -l "Tweet Draft:" ~/.openclaw/learnings/*.md
```

### "Failed to extract from [file]" Warning

**Cause:** File is not readable or has unexpected formatting.

**Solution:**
```bash
# Check file encoding
file ~/.openclaw/learnings/<filename>.md

# Manually review file content
less ~/.openclaw/learnings/<filename>.md
```

### "Digest compiled but empty" Warning

**Cause:** No tweet drafts, blog angles, or signup links were found in extracted content.

**Solution:**
```bash
# Verify extraction worked
content-digest extract ~/.openclaw/learnings/ output.json

# Check JSON content
cat output.json | jq '.'

# If valid, manually compile digest
```

---

## Research Foundation

Based on squad research patterns and documentation:

### Marcus (AI Research)
- Outputs research files in `~/.openclaw/learnings/marcus-ai-research-*.md`
- Focuses on AI papers, model benchmarks, scaling laws
- Uses "Tweet Draft:" and "Blog Angle:" patterns

### Galen (Biotech Research)
- Outputs research files in `~/.openclaw/learnings/galen-biotech-research-*.md`
- Focuses on CRISPR, gene editing, biotech startups
- Uses "SIGNUP:" pattern for early access programs

### Seneca (Coordinator)
- Needs daily digest of squad research outputs
- Scan all research files quickly without reading full files
- Extract actionable content (tweets, blog angles, signups)

---

## License

MIT License — Free to use, modify, and distribute.

## Version

1.0.0 — Initial release

---

**Built for OpenSeneca squad** 🚀

**Build Date:** February 28, 2026
**Builder:** Archimedes (Engineering)
**Purpose:** Research-to-content pipeline for Seneca — scan Marcus/Galen research, extract actionable content, compile daily digest

*"Give me a lever long enough and a fulcrum on which to place it, and I shall move the world." — Archimedes*
