# Voice-to-Note Application - Project Context

## 1. Project Purpose

The Voice-to-Note Application is a desktop utility designed to streamline the process of converting voice recordings made on a mobile phone into clean, readable markdown notes within an Obsidian knowledge management system.

**Primary Goals:**
- Convert .m4a audio recordings into high-quality text transcripts
- Automatically clean and format transcripts for readability
- Seamlessly integrate processed notes into an existing Obsidian vault

**Target User:**
A user who captures thoughts, ideas, and notes through voice recordings on their phone and wants these recordings automatically transformed into well-formatted markdown documents in their Obsidian vault on their PC.

## 2. Core Features

### 2.1 Audio File Processing
- Accept .m4a audio files as input
- Validate audio file format and integrity
- Handle multiple audio files in batch processing mode

### 2.2 LLM-Powered Transcription
- Utilize Large Language Model capabilities for accurate speech-to-text conversion
- Support for natural speech patterns and various accents
- Context-aware transcription for improved accuracy

### 2.3 Text Cleaning and Enhancement
- **Filler Word Removal**: Automatically detect and remove common filler words (um, uh, like, you know, etc.)
- **Punctuation Addition**: Intelligently add punctuation marks (periods, commas, question marks, etc.)
- **Sentence Structure**: Format text into proper sentences and paragraphs
- **Readability Enhancement**: Improve overall text flow and coherence

### 2.4 Markdown Output Generation
- Format transcripts as valid markdown documents
- Apply consistent formatting standards
- Include metadata (e.g., recording date, file name)

### 2.5 Obsidian Vault Integration
- Write processed markdown files directly to the user's Obsidian vault
- Maintain compatibility with Obsidian's file structure
- Support for custom folder organization within the vault

## 3. Functional Requirements

### FR-1: Audio File Ingestion
- **FR-1.1**: System shall accept .m4a audio files as input
- **FR-1.2**: System shall validate audio file format before processing
- **FR-1.3**: System shall provide clear error messages for invalid or corrupted files
- **FR-1.4**: System shall support drag-and-drop file selection
- **FR-1.5**: System shall support batch processing of multiple files

### FR-2: Transcription Processing
- **FR-2.1**: System shall transcribe audio content to text using an LLM
- **FR-2.2**: System shall maintain contextual accuracy in transcription
- **FR-2.3**: System shall handle various audio qualities and recording conditions
- **FR-2.4**: System shall preserve proper nouns and technical terms where possible

### FR-3: Text Post-Processing
- **FR-3.1**: System shall remove common filler words from transcripts
- **FR-3.2**: System shall add appropriate punctuation to unpunctuated text
- **FR-3.3**: System shall segment text into logical paragraphs
- **FR-3.4**: System shall capitalize sentences appropriately
- **FR-3.5**: System shall preserve intended meaning while improving readability

### FR-4: Output Generation
- **FR-4.1**: System shall generate valid markdown-formatted files
- **FR-4.2**: System shall include frontmatter with metadata (date, source file, processing timestamp)
- **FR-4.3**: System shall support configurable output templates
- **FR-4.4**: System shall generate unique, descriptive filenames for output files

### FR-5: File System Integration
- **FR-5.1**: System shall write output files to a specified Obsidian vault directory
- **FR-5.2**: System shall create necessary subdirectories if they don't exist
- **FR-5.3**: System shall handle file naming conflicts (append numbers, timestamps, etc.)
- **FR-5.4**: System shall preserve file permissions and timestamps appropriately

### FR-6: Configuration Management
- **FR-6.1**: System shall allow users to configure the target Obsidian vault path
- **FR-6.2**: System shall allow users to configure LLM API credentials
- **FR-6.3**: System shall support configuration profiles for different use cases
- **FR-6.4**: System shall validate configuration settings before processing

### FR-7: User Feedback and Logging
- **FR-7.1**: System shall display processing progress to the user
- **FR-7.2**: System shall provide success/failure notifications for each file
- **FR-7.3**: System shall log errors and warnings for troubleshooting
- **FR-7.4**: System shall estimate processing time for queued files

## 4. Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1**: System shall process a 5-minute audio file within 2 minutes (excluding LLM API latency)
- **NFR-1.2**: System shall maintain responsive UI during processing
- **NFR-1.3**: System shall efficiently handle batch processing without memory leaks
- **NFR-1.4**: System shall cache processed results to avoid re-processing

### NFR-2: Accuracy
- **NFR-2.1**: Transcription accuracy shall be at least 95% for clear audio recordings
- **NFR-2.2**: Filler word removal shall maintain semantic meaning of the original speech
- **NFR-2.3**: Punctuation addition shall result in grammatically correct sentences in 90%+ of cases

### NFR-3: Reliability
- **NFR-3.1**: System shall handle API failures gracefully with retry logic
- **NFR-3.2**: System shall not lose or corrupt input files during processing
- **NFR-3.3**: System shall maintain processing queue state across application restarts
- **NFR-3.4**: System shall validate output before writing to disk

### NFR-4: Usability
- **NFR-4.1**: User shall be able to process a file with no more than 3 clicks
- **NFR-4.2**: Configuration setup shall be intuitive and well-documented
- **NFR-4.3**: Error messages shall be clear and actionable
- **NFR-4.4**: System shall provide helpful tooltips and guidance

### NFR-5: Security and Privacy
- **NFR-5.1**: System shall store API credentials securely (encrypted storage)
- **NFR-5.2**: System shall not transmit audio files to third parties except the configured LLM service
- **NFR-5.3**: System shall allow users to opt-out of telemetry or usage tracking
- **NFR-5.4**: System shall handle user data in compliance with privacy best practices

### NFR-6: Maintainability
- **NFR-6.1**: Code shall be modular and follow separation of concerns
- **NFR-6.2**: System shall include comprehensive error handling
- **NFR-6.3**: Configuration shall be externalized (not hardcoded)
- **NFR-6.4**: System shall include adequate logging for debugging

### NFR-7: Compatibility
- **NFR-7.1**: System shall run on Windows, macOS, and Linux
- **NFR-7.2**: Output markdown shall be compatible with Obsidian v1.0+
- **NFR-7.3**: System shall handle various .m4a encoding formats

**Note**: For detailed technical architecture, components, data flow, and integration points, see [TECHNICAL.md](./TECHNICAL.md).

## 5. Assumptions

### 5.1 User Environment Assumptions
- **A-1**: User has an existing Obsidian vault on their PC
- **A-2**: User has a method to transfer .m4a files from phone to PC (USB, cloud sync, email, etc.)
- **A-3**: User has internet connectivity for API calls
- **A-4**: User is willing to obtain and configure LLM API credentials
- **A-5**: User's PC meets minimum system requirements (reasonable CPU, storage)

### 5.2 Audio File Assumptions
- **A-6**: Audio files are in .m4a format (AAC codec)
- **A-7**: Audio quality is sufficient for transcription (minimal background noise)
- **A-8**: Recordings are in a language supported by the chosen LLM
- **A-9**: Recordings are primarily a single speaker (the user)
- **A-10**: Recording length is typically under 30 minutes per file

### 5.3 Workflow Assumptions
- **A-11**: User manually initiates processing (not fully automated)
- **A-12**: User reviews and may edit transcripts after processing
- **A-13**: Processing doesn't need to be real-time (asynchronous is acceptable)
- **A-14**: User is comfortable with basic configuration (file paths, API keys)

### 5.4 Content Assumptions
- **A-15**: Recordings are general notes, thoughts, or ideas (not specialized medical/legal content)
- **A-16**: Filler word removal won't significantly alter meaning
- **A-17**: Basic markdown formatting is sufficient (no complex formatting needs)
- **A-18**: Metadata in frontmatter is useful but not critical

### 5.5 Technical Assumptions
- **A-19**: LLM APIs will remain stable and accessible
- **A-20**: API costs are acceptable for the user's usage volume
- **A-21**: Local storage space is sufficient for audio and markdown files
- **A-22**: Obsidian vault structure won't conflict with generated files

### 5.6 Privacy and Security Assumptions
- **A-23**: User consents to sending audio to third-party LLM services
- **A-24**: User is aware that transcripts may be retained by LLM providers (per their policies)
- **A-25**: No highly sensitive or confidential information in recordings
- **A-26**: Local storage of API keys is acceptable if encrypted

## 6. Future Enhancements (Out of Scope for Initial Version)

While not part of the initial requirements, the following enhancements could be considered for future iterations:

- **Speaker diarization**: Identify and label different speakers in multi-person recordings
- **Automatic tagging**: LLM-generated tags based on content for Obsidian organization
- **Summary generation**: Create TL;DR summaries for longer recordings
- **Mobile app integration**: Direct upload from phone app to processing service
- **Real-time processing**: Process recordings as they're being made
- **Multi-language support**: Automatic language detection and transcription
- **Custom vocabulary**: User-defined terms to improve transcription accuracy
- **Voice commands**: Embed voice commands in recording to control formatting
- **Integration with other note apps**: Support for Notion, Roam Research, etc.
- **Collaborative features**: Share processed notes with others

---

## Document Version
- **Version**: 1.0
- **Date**: 2025-11-24
- **Author**: Project Context Documentation
