# Voice-to-Note Application

Convert voice recordings from your phone into clean, formatted markdown notes for your Obsidian vault.

## Overview

Voice-to-Note is a Python-based desktop utility that transforms .m4a audio recordings into well-formatted markdown documents. It uses OpenAI's Whisper API for accurate transcription and GPT-4 for intelligent text cleanup, including filler word removal and proper punctuation.

## Features

- **High-Quality Transcription**: Leverages OpenAI Whisper API for accurate speech-to-text
- **Multi-Language Support**: Supports English, Chinese (Simplified), and mixed-language recordings with auto-detection
- **Intelligent Text Cleanup**: Removes language-appropriate filler words and adds proper punctuation using GPT-4
- **Seamless Obsidian Integration**: Writes formatted markdown directly to your Obsidian vault
- **Batch Processing**: Process multiple recordings at once
- **Rich CLI**: Beautiful command-line interface with progress bars and status updates
- **Configurable**: Customize filler words, formatting preferences, and output settings

## Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ffmpeg (for audio processing)
- An Obsidian vault

### Installing ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use chocolatey:
```bash
choco install ffmpeg
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voice-to-note-app.git
cd voice-to-note-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package:
```bash
pip install -e .
```

## Configuration

### First-Time Setup

Run the setup wizard:
```bash
voice-to-note setup
```

This will guide you through:
- Setting your OpenAI API key
- Configuring your Obsidian vault path
- Customizing processing preferences

### Manual Configuration

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-api-key-here
```

3. Copy the config template to your user config directory:
```bash
mkdir -p ~/.config/voice-to-note
cp config/config.yaml.template ~/.config/voice-to-note/config.yaml
```

4. Edit `~/.config/voice-to-note/config.yaml` and set your vault path:
```yaml
obsidian:
  vault_path: "/path/to/your/vault"
  output_folder: "Voice Notes"
```

## Usage

### Process a Single Recording

```bash
voice-to-note process recording.m4a
```

### Process Multiple Recordings

**Separate files (default):**
```bash
voice-to-note process recording1.m4a recording2.m4a recording3.m4a
```

Or use wildcards:
```bash
voice-to-note process *.m4a
```

**Combined into one note:**
```bash
voice-to-note process --combined recording1.m4a recording2.m4a recording3.m4a
```

Or combine all recordings in a directory:
```bash
voice-to-note process --combined *.m4a
```

### View Configuration

```bash
voice-to-note config --show
```

### Update Configuration

```bash
voice-to-note config --set vault_path=/new/path/to/vault
voice-to-note config --set output_folder="Daily Notes"
```

## Output Format

### Single Recording

Generated markdown files include frontmatter with metadata:

```markdown
---
created: 2025-11-24T10:30:00+13:00
source: recording_001.m4a
processed: 2025-11-24T10:32:15+13:00
duration: 5m 23s
---

Your transcribed and cleaned content appears here, properly formatted with
punctuation and paragraph breaks.

The text is cleaned of filler words while preserving the natural tone and
meaning of your recording.
```

### Combined Recordings (--combined mode)

When using `--combined`, multiple recordings are merged into a single note:

```markdown
---
created: 2025-11-25T10:00:00+13:00
sources:
  - recording1.m4a
  - recording2.m4a
  - recording3.m4a
processed: 2025-11-25T10:15:30+13:00
total_duration: 8m 45s
recordings: 3
---

## Recording 1: recording1.m4a
*11/25/2025 10:00 AM • 2m 30s*

[Transcribed content from first recording...]

## Recording 2: recording2.m4a
*11/25/2025 10:05 AM • 3m 15s*

[Transcribed content from second recording...]

## Recording 3: recording3.m4a
*11/25/2025 10:10 AM • 3m 00s*

[Transcribed content from third recording...]
```

## Multi-Language Support

Voice-to-Note supports both English and Chinese (Simplified) recordings:

### Language Auto-Detection (Recommended)

By default, the application auto-detects the language of your recording. This works great for:
- Pure English recordings
- Pure Chinese recordings  
- Mixed recordings (code-switching between English and Chinese)

### Manual Language Selection

You can also specify the language explicitly in your config:

```yaml
llm:
  transcription:
    language: "en"  # For English
    # or
    language: "zh"  # For Chinese (Simplified)
```

### Filler Word Removal

The application includes separate filler word lists for each language:

**English**: um, uh, like, you know, sort of, kind of  
**Chinese**: 呃, 嗯, 那个, 就是, 然后, 这个, 其实, 对

Both lists are applied during processing, making it ideal for bilingual speakers.

### Mixed-Language Example

If your recording contains both English and Chinese (code-switching), the application will:
1. Auto-detect and transcribe both languages correctly
2. Remove filler words from both languages
3. Apply language-appropriate punctuation (e.g., 。for Chinese, . for English)
4. Preserve the original language mix without translation

Example output:
```markdown
Today I learned about 机器学习. It's really interesting because 它可以帮助我们
solve complex problems. 我觉得 this technology will be很重要 in the future.
```

## Batch Processing Modes

Voice-to-Note supports two modes for processing multiple recordings:

### Separate Files Mode (Default)

Each recording is processed into its own markdown file:
```bash
voice-to-note process *.m4a
# Creates: 2025-11-25-100000-voice-note.md
#          2025-11-25-100100-voice-note.md
#          2025-11-25-100200-voice-note.md
```

Use this when:
- Recordings cover different topics
- You want to organize notes separately in Obsidian
- Each recording stands alone

### Combined Mode

All recordings are merged into a single markdown file with sections:
```bash
voice-to-note process --combined *.m4a
# Creates: 2025-11-25-combined-notes.md (with all recordings)
```

Use this when:
- Multiple parts of the same meeting or lecture
- Sequential thoughts on the same topic
- Daily voice journal entries you want in one note
- Related voice memos throughout the day

## Configuration Options

See `config/config.yaml.template` for all available options, including:

- **Language**: Set to 'en', 'zh', or null for auto-detection
- **Filler Words**: Separate lists for English and Chinese filler words
- **Aggressiveness**: Control how aggressively filler words are removed (low/moderate/high)
- **Formatting**: Paragraph structure, heading detection
- **Filenames**: Patterns for single and combined output file names
- **Logging**: Log level and file location

## API Costs

This application uses OpenAI's APIs:
- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4 API**: ~$0.01-0.03 per request (varies by text length)

A typical 5-minute recording costs approximately $0.03-0.05 to process.

## Troubleshooting

### "ffmpeg not found" error
Install ffmpeg using the instructions in the Prerequisites section.

### "Invalid API key" error
Ensure your OpenAI API key is correctly set in `.env` and has sufficient credits.

### "Vault path not found" error
Verify the vault path in your config file exists and is accessible.

### Transcription quality issues
- Ensure audio quality is good (minimal background noise)
- For best results with Chinese, use auto-detection (language: null)
- For mixed-language recordings, auto-detection is recommended
- Try re-recording with better audio equipment
- Speak clearly and at a moderate pace

### Chinese characters not displaying correctly
- Ensure your terminal/editor supports UTF-8 encoding
- Check that your Obsidian vault uses UTF-8 encoding
- Verify Chinese fonts are installed on your system

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

```
src/
├── audio_handler.py        # Audio file validation and metadata
├── transcription_service.py # OpenAI Whisper API integration
├── text_processor.py       # Filler word removal and text cleanup
├── markdown_formatter.py   # Markdown generation with frontmatter
├── file_writer.py          # Write to Obsidian vault
├── config_manager.py       # Configuration loading and validation
├── pipeline.py             # Orchestrate the full processing pipeline
└── cli.py                  # Command-line interface
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [OpenAI Whisper](https://openai.com/research/whisper) for transcription
- Uses [OpenAI GPT-4](https://openai.com/gpt-4) for text processing
- CLI powered by [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
