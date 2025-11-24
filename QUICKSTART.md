# Quick Start Guide

Get up and running with Voice-to-Note in 5 minutes!

## Step 1: Install Dependencies

Make sure you have Python 3.9+ and ffmpeg installed.

### Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Step 2: Run Setup Wizard

The easiest way to configure Voice-to-Note:

```bash
voice-to-note setup
```

This will guide you through:
1. Setting your OpenAI API key
2. Configuring your Obsidian vault path
3. Choosing processing preferences

## Step 3: Process Your First Recording

```bash
voice-to-note process your-recording.m4a
```

That's it! Your processed note will appear in your Obsidian vault.

### Multi-Language Support

Voice-to-Note automatically detects and supports:
- **English recordings**
- **Chinese (Simplified) recordings** - 支持简体中文录音
- **Mixed-language recordings** - Perfect for bilingual speakers who code-switch

**Example - Chinese recording:**
```bash
voice-to-note process 中文录音.m4a
```

**Example - Mixed English/Chinese:**
```bash
voice-to-note process bilingual-notes.m4a
```

The application will:
1. Auto-detect the language(s) in your recording
2. Remove appropriate filler words for each language
3. Apply correct punctuation (。for Chinese, . for English)
4. Preserve the language mix without translation

## Common Commands

### Process Multiple Files

**Separate notes (default):**
```bash
voice-to-note process *.m4a
```

**Combined into one note:**
```bash
voice-to-note process --combined *.m4a
```

### View Configuration

```bash
voice-to-note config --show
```

### Update Configuration

```bash
voice-to-note config --set obsidian.vault_path /new/path
voice-to-note config --set processing.remove_aggressiveness high
```

## Manual Configuration (Alternative to Setup Wizard)

### 1. Create .env file

```bash
cp .env.template .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

### 2. Create config file

```bash
mkdir -p ~/.config/voice-to-note
cp config/config.yaml.template ~/.config/voice-to-note/config.yaml
```

Edit `~/.config/voice-to-note/config.yaml` and set your vault path:
```yaml
obsidian:
  vault_path: "/path/to/your/vault"
```

## Troubleshooting

### "ffmpeg not found"
Install ffmpeg using the instructions above.

### "Configuration Error: Obsidian vault path not configured"
Run `voice-to-note setup` or manually set the vault path.

### "API key not found"
Make sure your `.env` file exists and contains a valid OpenAI API key.

## Example Output

### Single Recording - English
```markdown
---
created: 2025-11-24T10:30:00+13:00
source: meeting-notes.m4a
---

Today we discussed the new project timeline. The main challenges are resource
allocation and the tight deadline. We need to prioritize the core features
and postpone the nice-to-have items.
```

### Single Recording - Chinese
```markdown
---
created: 2025-11-24T10:30:00+13:00
source: 中文笔记.m4a
---

今天我学习了机器学习的基础知识。主要内容包括监督学习和非监督学习的
区别。我觉得这个领域非常有趣，值得深入研究。
```

### Single Recording - Mixed Language
```markdown
---
created: 2025-11-24T10:30:00+13:00
source: bilingual-notes.m4a
---

Today I learned about 机器学习 algorithms. The key difference between
supervised and unsupervised learning is 标签数据的使用. I think this field
has great potential for 未来的发展.
```

### Combined Mode - Multiple Recordings
```markdown
---
created: 2025-11-25T09:00:00+13:00
sources:
  - morning-thoughts.m4a
  - afternoon-ideas.m4a
  - evening-reflection.m4a
processed: 2025-11-25T18:30:00+13:00
total_duration: 12m 45s
recordings: 3
---

## Recording 1: morning-thoughts.m4a
*11/25/2025 09:00 AM • 4m 20s*

This morning I had some interesting ideas about the project architecture.
We should consider using a microservices approach instead of a monolithic
design. This would give us more flexibility.

## Recording 2: afternoon-ideas.m4a
*11/25/2025 02:15 PM • 5m 10s*

Building on this morning's thoughts, I realized we could implement the
authentication service first. This would be a good proof of concept for
the microservices pattern.

## Recording 3: evening-reflection.m4a
*11/25/2025 06:45 PM • 3m 15s*

After thinking about it all day, I'm convinced this is the right approach.
Tomorrow I'll start drafting a proposal for the team.
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize your configuration in `~/.config/voice-to-note/config.yaml`
- Check the Multi-Language Support section in README for more details
- Customize Chinese filler words in your config if needed

## Support

For issues or questions, please refer to the README.md troubleshooting section.
