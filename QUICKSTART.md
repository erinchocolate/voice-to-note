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

## Common Commands

### Process Multiple Files

```bash
voice-to-note process *.m4a
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

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize your configuration in `~/.config/voice-to-note/config.yaml`
- Check the example workflow in the README

## Support

For issues or questions, please refer to the README.md troubleshooting section.
