"""Text processing for cleaning and formatting transcripts."""

import logging
import re
from typing import List, Optional
from openai import OpenAI, APIError

logger = logging.getLogger(__name__)


class TextProcessingError(Exception):
    """Raised when text processing fails."""
    pass


class TextProcessor:
    """Processes transcribed text to remove fillers and improve formatting."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        filler_words_english: Optional[List[str]] = None,
        filler_words_chinese: Optional[List[str]] = None,
        aggressiveness: str = "moderate"
    ):
        """
        Initialize text processor.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use
            filler_words_english: List of English filler words to remove
            filler_words_chinese: List of Chinese filler words to remove
            aggressiveness: How aggressive to be ('low', 'moderate', 'high')
        """
        self.api_key = api_key
        self.model = model
        self.filler_words_english = filler_words_english or [
            "um", "uh", "like", "you know", "sort of", "kind of"
        ]
        self.filler_words_chinese = filler_words_chinese or [
            "呃", "嗯", "那个", "就是", "然后", "这个", "其实", "对"
        ]
        # Combine both lists for pattern matching
        self.filler_words = self.filler_words_english + self.filler_words_chinese
        self.aggressiveness = aggressiveness
        self.client = OpenAI(api_key=api_key)
        
        logger.info(f"Initialized text processor with model {model} (bilingual support)")
    
    def process(self, raw_text: str) -> str:
        """
        Process raw transcript text.
        
        Args:
            raw_text: Raw transcribed text
            
        Returns:
            Cleaned and formatted text
            
        Raises:
            TextProcessingError: If processing fails
        """
        logger.info("Starting text processing")
        
        # First pass: pattern-based filler word removal
        text = self._remove_filler_words_pattern(raw_text)
        
        # Second pass: GPT-based cleanup and formatting
        text = self._process_with_gpt(text)
        
        logger.info("Text processing completed")
        return text
    
    def _remove_filler_words_pattern(self, text: str) -> str:
        """
        Remove obvious filler words using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            Text with filler words removed
        """
        if self.aggressiveness == "low":
            # Only remove very obvious fillers at sentence starts
            return text
        
        result = text
        
        for filler in self.filler_words:
            # Create regex patterns for different contexts
            patterns = []
            
            if self.aggressiveness in ["moderate", "high"]:
                # Remove filler words at sentence boundaries
                patterns.append(rf'\b{re.escape(filler)}\b[,\s]+')
                patterns.append(rf'[,\s]+\b{re.escape(filler)}\b(?=[,.\s])')
            
            if self.aggressiveness == "high":
                # More aggressive: remove all instances
                patterns.append(rf'\b{re.escape(filler)}\b')
            
            for pattern in patterns:
                result = re.sub(pattern, ' ', result, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\s+([.,!?])', r'\1', result)
        
        return result.strip()
    
    def _process_with_gpt(self, text: str) -> str:
        """
        Process text with GPT for punctuation and formatting.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned and formatted text
            
        Raises:
            TextProcessingError: If GPT processing fails
        """
        logger.debug("Processing text with GPT")
        
        # Build prompt based on aggressiveness
        system_prompt = self._build_system_prompt()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,  # Lower temperature for more consistent formatting
                max_tokens=4000
            )
            
            cleaned_text = response.choices[0].message.content.strip()
            
            if not cleaned_text:
                raise TextProcessingError("GPT returned empty response")
            
            word_count = len(cleaned_text.split())
            logger.info(f"GPT processing completed ({word_count} words)")
            
            return cleaned_text
            
        except APIError as e:
            raise TextProcessingError(f"OpenAI API error during text processing: {e}") from e
        except Exception as e:
            raise TextProcessingError(f"Unexpected error during text processing: {e}") from e
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt for GPT based on settings.
        
        Returns:
            System prompt string
        """
        base_prompt = """You are a professional text editor specializing in cleaning voice transcripts in both English and Chinese (Simplified).

Your task is to take raw voice transcript text and transform it into clean, readable text suitable for note-taking.

CRITICAL LANGUAGE RULES:
- The text may be in English, Chinese, or mixed (code-switching between both)
- PRESERVE the original language(s) - DO NOT translate
- If text is mixed, keep English parts in English and Chinese parts in Chinese
- Apply language-appropriate punctuation:
  * English: . , ! ? ; :
  * Chinese: 。，！？；：
- Respect language-specific formatting conventions

GENERAL INSTRUCTIONS:
1. Add appropriate punctuation based on the language being used
2. Organize the text into logical paragraphs
3. Capitalize sentences properly (for English text)
4. Fix any obvious transcription errors
5. Maintain the speaker's original meaning and tone
6. Keep the natural, conversational voice
7. For mixed language text, maintain natural flow between languages
8. Return ONLY the cleaned text with no additional commentary or explanations
"""
        
        if self.aggressiveness == "low":
            base_prompt += "\n9. Remove only the most obvious filler words if they disrupt readability"
        elif self.aggressiveness == "moderate":
            base_prompt += "\n9. Remove common filler words while preserving natural speech patterns"
        else:  # high
            base_prompt += "\n9. Aggressively remove all filler words and verbal tics to create polished, professional text"
        
        # Create language-specific filler lists
        english_fillers = ", ".join(self.filler_words_english)
        chinese_fillers = "、".join(self.filler_words_chinese)
        
        base_prompt += f"\n\nEnglish filler words to watch for: {english_fillers}"
        base_prompt += f"\nChinese filler words to watch for: {chinese_fillers}"
        
        base_prompt += "\n\nRemember: Preserve the original language(s). Return ONLY the cleaned text, nothing else."
        
        return base_prompt
    
    def estimate_cost(self, text: str) -> float:
        """
        Estimate processing cost in USD.
        
        Args:
            text: Input text
            
        Returns:
            Estimated cost in USD
        """
        # Rough token estimation (1 token ≈ 4 characters)
        chars = len(text)
        tokens = chars / 4
        
        # GPT-4 Turbo pricing (as of 2024):
        # Input: $0.01 per 1K tokens
        # Output: $0.03 per 1K tokens (assume similar length output)
        input_cost = (tokens / 1000) * 0.01
        output_cost = (tokens / 1000) * 0.03
        
        return input_cost + output_cost
