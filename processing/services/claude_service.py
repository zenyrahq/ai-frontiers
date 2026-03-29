"""
Claude API Service
Handles content summarization, translation and analysis using Claude API
"""
import asyncio
from typing import Optional, Dict, Any, List
from anthropic import AsyncAnthropic
from loguru import logger
from dataclasses import dataclass
import json


@dataclass
class ProcessedContent:
    """Processed content result"""
    summary: str
    keywords: List[str]
    entities: List[str]
    category: str
    importance_score: float
    sentiment: str
    translation: Optional[Dict[str, str]] = None


class ClaudeService:
    """
    Claude API service for content processing

    Provides:
    - Content summarization
    - Keyword extraction
    - Entity recognition
    - Category classification
    - Importance scoring
    - Multi-language translation
    """

    def __init__(self, api_key: str):
        """
        Initialize Claude service

        Args:
            api_key: Anthropic API key
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1000

    async def process_content(
        self,
        title: str,
        abstract: str,
        categories: List[str] = None,
        target_languages: List[str] = None
    ) -> ProcessedContent:
        """
        Process a single content item

        Args:
            title: Content title
            abstract: Content abstract/description
            categories: Existing categories (optional)
            target_languages: Languages for translation (optional)

        Returns:
            ProcessedContent object with analysis results
        """
        try:
            # Build prompt
            prompt = self._build_processing_prompt(title, abstract, categories)

            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            result = self._parse_response(response.content[0].text)

            # Add translations if requested
            if target_languages:
                result.translation = await self._translate_content(
                    title=title,
                    abstract=abstract,
                    summary=result.summary,
                    languages=target_languages
                )

            logger.debug(f"Processed: {title[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error processing content: {e}")
            # Return default values
            return ProcessedContent(
                summary=abstract[:200],
                keywords=[],
                entities=[],
                category="general",
                importance_score=0.5,
                sentiment="neutral"
            )

    def _build_processing_prompt(
        self,
        title: str,
        abstract: str,
        categories: List[str] = None
    ) -> str:
        """
        Build prompt for Claude API

        Args:
            title: Content title
            abstract: Content abstract
            categories: Existing categories

        Returns:
            Formatted prompt string
        """
        category_hint = f"\nExisting categories: {', '.join(categories)}" if categories else ""

        prompt = f"""Analyze the following AI research paper and provide structured information.

Title: {title}

Abstract: {abstract}
{category_hint}

Please provide a JSON response with the following structure:
{{
    "summary": "A concise 2-3 sentence summary in Chinese",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "entities": ["entity1", "entity2", "entity3"],
    "category": "primary_category",
    "importance_score": 0.85,
    "sentiment": "positive/neutral/negative"
}}

Requirements:
1. summary: 2-3 sentences in Chinese, capture key contributions
2. keywords: 5-10 most important technical terms
3. entities: Model names, company names, person names, technologies
4. category: One of: artificial_intelligence, machine_learning, natural_language_processing, computer_vision, robotics, neural_computing, general
5. importance_score: Float between 0-1, based on novelty, impact, relevance
6. sentiment: Overall sentiment of the paper

Return ONLY the JSON object, no other text."""

        return prompt

    def _parse_response(self, response_text: str) -> ProcessedContent:
        """
        Parse Claude API response

        Args:
            response_text: Raw API response

        Returns:
            ProcessedContent object
        """
        try:
            # Clean response (remove markdown code blocks if present)
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            # Parse JSON
            data = json.loads(clean_text.strip())

            return ProcessedContent(
                summary=data.get("summary", ""),
                keywords=data.get("keywords", []),
                entities=data.get("entities", []),
                category=data.get("category", "general"),
                importance_score=float(data.get("importance_score", 0.5)),
                sentiment=data.get("sentiment", "neutral")
            )

        except Exception as e:
            logger.warning(f"Failed to parse Claude response: {e}")
            # Return safe defaults
            return ProcessedContent(
                summary="",
                keywords=[],
                entities=[],
                category="general",
                importance_score=0.5,
                sentiment="neutral"
            )

    async def _translate_content(
        self,
        title: str,
        abstract: str,
        summary: str,
        languages: List[str]
    ) -> Dict[str, str]:
        """
        Translate content to multiple languages

        Args:
            title: Original title
            abstract: Original abstract
            summary: Generated summary
            languages: Target language codes (en, ja, etc.)

        Returns:
            Dictionary of translations by language
        """
        translations = {}

        for lang in languages:
            try:
                lang_names = {
                    "en": "English",
                    "ja": "Japanese",
                    "zh": "Chinese"
                }

                prompt = f"""Translate the following text to {lang_names.get(lang, lang)}.

Title: {title}

Summary: {summary}

Provide only the translated text in this format:
Title: [translated title]
Summary: [translated summary]"""

                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                translations[lang] = response.content[0].text
                logger.debug(f"Translated to {lang}")

            except Exception as e:
                logger.error(f"Translation error for {lang}: {e}")
                translations[lang] = ""

        return translations

    async def batch_process(
        self,
        contents: List[Dict[str, Any]],
        batch_size: int = 5
    ) -> List[ProcessedContent]:
        """
        Process multiple contents in batches

        Args:
            contents: List of content dictionaries
            batch_size: Number of concurrent requests

        Returns:
            List of ProcessedContent objects
        """
        results = []

        for i in range(0, len(contents), batch_size):
            batch = contents[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} items)")

            # Process batch concurrently
            tasks = [
                self.process_content(
                    title=item["title"],
                    abstract=item["abstract"],
                    categories=item.get("categories")
                )
                for item in batch
            ]

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Small delay to avoid rate limiting
            await asyncio.sleep(1)

        logger.info(f"Processed {len(results)} items total")
        return results
