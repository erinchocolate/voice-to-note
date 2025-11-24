# Voice-to-Note Application - Technical Documentation

This document contains the technical architecture, components, data flow, and integration details for the Voice-to-Note application. For project overview, requirements, and assumptions, see [ABOUT.md](./ABOUT.md).

---

## 1. Technical Considerations

### 1.1 LLM Service Selection
**Transcription Options:**
- **OpenAI Whisper API**: Industry-leading speech-to-text accuracy, supports multiple languages
- **AssemblyAI**: Good accuracy with speaker diarization capabilities
- **Google Cloud Speech-to-Text**: Robust option with good language support
- **Local Whisper Model**: Privacy-focused, no API costs, but requires local GPU

**Text Processing Options:**
- **OpenAI GPT-4/GPT-4-Turbo**: Excellent at text cleanup, punctuation, and formatting
- **Claude 3**: Strong text processing capabilities with large context windows
- **Local LLM (Llama 3, Mistral)**: Privacy-focused option for text post-processing

**Recommended Approach:**
- Use Whisper API for transcription (accuracy & reliability)
- Use GPT-4 or Claude for text cleanup and formatting
- Provide configuration options to switch providers

### 1.2 Multi-Language Support
**Supported Languages:**
- **English**: Full support with native filler word detection
- **Chinese (Simplified)**: Full support with Chinese-specific filler word detection
- **Mixed Language**: Auto-detection handles code-switching between English and Chinese

**Language Detection:**
- Whisper API provides auto-detection when `language=null`
- Recommended approach for mixed-language recordings
- Can be manually overridden in config (`language: 'en'` or `language: 'zh'`)

**Text Processing Challenges:**
- Filler words differ significantly between languages
- Punctuation marks differ (English: . , ! ? vs Chinese: 。，！？)
- GPT must preserve original language(s) without translation
- Mixed-language text requires careful handling to maintain natural flow

### 1.3 Audio Format Handling
- **Library Recommendation**: Use `pydub` (Python) or `ffmpeg` bindings for audio processing
- **Format Support**: Primary support for .m4a, with potential extension to MP3, WAV, FLAC
- **Pre-processing**: May need to convert or normalize audio for optimal transcription

### 1.4 File System Operations
- **Path Management**: Use `pathlib` for cross-platform path handling
- **File Watching**: Optional feature to monitor a folder for new recordings
- **Vault Discovery**: Support manual configuration or auto-detection of Obsidian vaults

### 1.5 Configuration Management
**Configuration File Format**: JSON or YAML
**Required Settings:**
- LLM API keys and endpoints
- Obsidian vault path
- Output folder within vault
- Processing preferences (filler word aggressiveness, formatting style)

**Configuration Location:**
- User config directory (`~/.config/voice-to-note/` on Linux/Mac, `AppData` on Windows)
- Support for environment variables for API keys

### 1.6 Error Handling Strategy
- Validate inputs before processing
- Implement retry logic for API calls (with exponential backoff)
- Graceful degradation if certain features fail
- Comprehensive error logging with context

### 1.7 Development Stack Recommendations
**Primary Option - Python:**
- **Pros**: Excellent LLM library support, rich ecosystem for audio processing
- **Libraries**: `openai`, `anthropic`, `pydub`, `pathlib`, `pyyaml`
- **UI**: `tkinter` for simple GUI, or `PyQt`/`PySide` for richer interface

**Alternative - TypeScript/Node.js:**
- **Pros**: Modern web technologies, Electron for cross-platform desktop apps
- **Libraries**: `openai` SDK, `fluent-ffmpeg`, `node-whisper`
- **UI**: Electron + React for modern, responsive interface

**Recommended**: Python for simplicity and library support, with a tkinter or command-line interface

## 2. Components/Subsystems

### 2.1 Audio File Handler
**Responsibilities:**
- Accept audio files from user (drag-drop, file picker, folder watch)
- Validate file format and integrity
- Extract metadata (duration, bitrate, recording date)
- Queue files for processing

**Interfaces:**
- Input: File paths or File objects
- Output: Validated audio file objects with metadata

### 2.2 LLM Transcription Service
**Responsibilities:**
- Interface with speech-to-text LLM API
- Handle API authentication and rate limiting
- Manage errors and retries
- Return raw transcript text

**Interfaces:**
- Input: Audio file data or path
- Output: Raw transcript text string

### 2.3 Text Processor
**Responsibilities:**
- Remove filler words using pattern matching and LLM context (multi-language)
- Add language-appropriate punctuation using LLM
- Format into paragraphs
- Improve readability while preserving meaning and original language(s)
- Handle mixed-language text without translation

**Interfaces:**
- Input: Raw transcript text (may be English, Chinese, or mixed)
- Output: Cleaned and formatted text (preserving original languages)

**Sub-components:**
- Filler Word Remover (English + Chinese patterns)
- Punctuation Engine (language-aware)
- Paragraph Formatter

**Language Handling:**
- Maintains separate filler word lists for English and Chinese
- Applies both pattern-matching and LLM-based removal
- GPT system prompt explicitly instructs to preserve original languages
- Handles code-switching gracefully

### 2.4 Markdown Formatter
**Responsibilities:**
- Convert processed text to markdown format
- Add frontmatter with metadata
- Apply markdown conventions (headings, lists if detected)
- Generate final markdown content

**Interfaces:**
- Input: Cleaned text + metadata
- Output: Complete markdown document string

### 2.5 File System Writer
**Responsibilities:**
- Write markdown content to specified Obsidian vault
- Handle file naming (timestamps, original filename)
- Resolve naming conflicts
- Create necessary directories
- Verify successful write operations

**Interfaces:**
- Input: Markdown content + vault path + preferences
- Output: File path of created document

### 2.6 Configuration Manager
**Responsibilities:**
- Load and validate configuration files
- Provide configuration to other components
- Update configuration when user changes settings
- Manage API credentials securely

**Interfaces:**
- Methods to get/set configuration values
- Validation of configuration completeness

### 2.7 User Interface Layer
**Responsibilities:**
- Provide file selection mechanisms
- Display processing progress
- Show success/error notifications
- Allow configuration editing
- Display processing queue

**Interfaces:**
- User interactions (clicks, file drops)
- Display updates (progress bars, status messages)

## 3. Data Flow

### 3.1 High-Level Processing Pipeline

```
[User's Phone] → (Transfer) → [.m4a File on PC]
                                      ↓
                              [Audio File Handler]
                                      ↓
                           (Validate and Queue)
                                      ↓
                         [LLM Transcription Service]
                                      ↓
                            (Raw Transcript Text)
                                      ↓
                              [Text Processor]
                                      ↓
                     (Cleaned, Punctuated Text)
                                      ↓
                           [Markdown Formatter]
                                      ↓
                         (Complete .md Document)
                                      ↓
                           [File System Writer]
                                      ↓
                    [Obsidian Vault/.../note.md]
```

### 3.2 Detailed Processing Steps

**Step 1: File Ingestion**
- User selects .m4a file(s) via UI or drops into watched folder
- Audio File Handler validates format
- File added to processing queue

**Step 2: Transcription**
- Audio file sent to LLM transcription service (e.g., Whisper API)
- API returns raw transcript as plain text
- Transcript stored with original filename reference

**Step 3: Text Cleaning**
- Raw transcript passed to Text Processor
- Filler Word Remover identifies and removes patterns
- Punctuation Engine (LLM-based) adds appropriate punctuation
- Paragraph Formatter segments text into logical blocks

**Step 4: Markdown Generation**
- Cleaned text passed to Markdown Formatter
- Frontmatter created with metadata:
  ```yaml
  ---
  created: 2025-11-24T06:10:50+13:00
  source: recording_001.m4a
  processed: 2025-11-24T06:12:30+13:00
  ---
  ```
- Text formatted as markdown body

**Step 5: File Output**
- Complete markdown document passed to File System Writer
- Target path determined (vault path + subfolder + filename)
- File written to disk
- Success notification shown to user

### 3.3 Error Flow
- Any component encountering an error logs the issue
- User notified via UI with actionable error message
- Failed items remain in queue for retry or manual review
- Processing continues with next item in queue

## 4. Integration Points

### 4.1 LLM API Integration

**Transcription Service (e.g., OpenAI Whisper)**
- **Endpoint**: `https://api.openai.com/v1/audio/transcriptions`
- **Authentication**: API key in Authorization header
- **Input Format**: Multi-part form data with audio file
- **Output Format**: JSON with transcript text
- **Rate Limits**: Monitor and respect API rate limits
- **Error Handling**: Retry on 429, fail on 4xx, retry on 5xx

**Text Processing Service (e.g., OpenAI GPT-4)**
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Authentication**: API key in Authorization header
- **Input Format**: JSON with system prompt + user transcript
- **Output Format**: JSON with cleaned text
- **Prompt Engineering**: Critical for quality - include clear instructions

**Example Prompt for Text Cleaning (Bilingual):**
```
You are a professional text editor specializing in cleaning voice transcripts 
in both English and Chinese (Simplified).

CRITICAL LANGUAGE RULES:
- The text may be in English, Chinese, or mixed (code-switching between both)
- PRESERVE the original language(s) - DO NOT translate
- Apply language-appropriate punctuation:
  * English: . , ! ? ; :
  * Chinese: 。，！？；：

GENERAL INSTRUCTIONS:
1. Add appropriate punctuation based on the language being used
2. Organize the text into logical paragraphs
3. Remove filler words while preserving natural speech patterns
4. Maintain the speaker's original meaning and tone
5. Return ONLY the cleaned text, nothing else

English filler words: um, uh, like, you know, sort of, kind of
Chinese filler words: 呃, 嗯, 那个, 就是, 然后, 这个, 其实, 对

Transcript:
{raw_transcript}
```

### 4.2 File System Integration

**Obsidian Vault Structure**
- Vault root directory (user-configured)
- Subdirectory for voice notes (e.g., `Voice Notes/` or `Daily Notes/`)
- Individual markdown files with timestamps or descriptive names

**File Naming Convention:**
- `YYYY-MM-DD-HHmmss-voice-note.md` (timestamp-based)
- `recording_name.md` (based on original audio filename)
- User-configurable patterns

**File Writing Process:**
1. Verify vault path exists and is writable
2. Create subdirectory if needed
3. Generate unique filename (handle conflicts)
4. Write markdown content
5. Verify file was written successfully
6. Optionally set file modification time to recording time

### 4.3 Configuration File Integration

**Configuration Storage:**
- Location: `~/.config/voice-to-note/config.yaml`
- Format: YAML for human readability

**Example Configuration (with Multi-Language Support):**
```yaml
obsidian:
  vault_path: "/home/user/Documents/MyVault"
  output_folder: "Voice Notes"
  filename_pattern: "{date}-voice-note"

llm:
  transcription:
    provider: "openai_whisper"
    api_key_env: "OPENAI_API_KEY"
    model: "whisper-1"
    language: null  # Auto-detect (recommended for mixed EN/CN)
  
  text_processing:
    provider: "openai_gpt"
    api_key_env: "OPENAI_API_KEY"
    model: "gpt-4-turbo-preview"

processing:
  # Separate filler word lists for each language
  filler_words_english:
    - "um"
    - "uh"
    - "like"
    - "you know"
  
  filler_words_chinese:
    - "呃"      # uh
    - "嗯"      # um/hmm
    - "那个"    # that/um
    - "就是"    # is (as filler)
    - "然后"    # then (overused)
    - "这个"    # this (as filler)
  
  remove_aggressiveness: "moderate"  # low, moderate, high
  add_headings: false
  paragraph_min_sentences: 2

logging:
  level: "INFO"
  file: "~/.config/voice-to-note/logs/app.log"
```

### 4.4 External Dependencies

**Required APIs:**
- OpenAI API (or alternative for transcription/text processing)

**System Requirements:**
- Python 3.9+ (if Python implementation)
- ffmpeg (for audio processing)
- Internet connection (for API calls)

**Optional Integrations:**
- File system watcher for automatic processing
- Obsidian plugins for enhanced workflow
- Cloud storage sync (Dropbox, Google Drive) for audio file transfer

---

## Document Version
- **Version**: 1.0
- **Date**: 2025-11-24
- **Author**: Technical Documentation
