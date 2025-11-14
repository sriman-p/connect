"""
Google Gemini AI Service
Handles interactions with Google's Gemini API
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from django.conf import settings
from .models import AIInteraction, AIModelConfig

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self, workspace=None, api_key: Optional[str] = None):
        """
        Initialize Gemini service.

        Args:
            workspace: Workspace object (optional, for per-workspace config)
            api_key: API key override (optional)
        """
        self.workspace = workspace

        # Get API key from workspace config, parameter, or settings
        if workspace and hasattr(workspace, 'ai_configs'):
            config = workspace.ai_configs.filter(is_active=True).first()
            if config and config.api_key:
                api_key = config.api_key

        if not api_key:
            api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY', ''))

        if not api_key:
            raise ValueError("Gemini API key not configured")

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Get model name
        model_name = 'gemini-pro'
        if workspace and hasattr(workspace, 'ai_configs'):
            config = workspace.ai_configs.filter(is_active=True).first()
            if config:
                model_name = config.model_name

        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def generate_completion(
        self,
        prompt: str,
        user,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate text completion.

        Args:
            prompt: Input prompt
            user: User making the request
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            context: Additional context data

        Returns:
            Dict with response and metadata
        """
        start_time = time.time()

        try:
            # Generate content
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens or 1000,
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract response text
            response_text = response.text if hasattr(response, 'text') else ''

            # Estimate tokens (rough estimate)
            tokens_used = len(prompt.split()) + len(response_text.split())

            # Log interaction
            if self.workspace:
                AIInteraction.objects.create(
                    workspace=self.workspace,
                    user=user,
                    interaction_type='completion',
                    prompt=prompt,
                    response=response_text,
                    model_used=self.model_name,
                    tokens_used=tokens_used,
                    duration_ms=duration_ms,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    context_data=context or {}
                )

            return {
                'success': True,
                'text': response_text,
                'tokens_used': tokens_used,
                'duration_ms': duration_ms,
                'model': self.model_name
            }

        except Exception as e:
            logger.error(f"Gemini completion error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'tokens_used': 0,
                'duration_ms': int((time.time() - start_time) * 1000)
            }

    def generate_summary(
        self,
        content: str,
        user,
        max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Generate content summary.

        Args:
            content: Content to summarize
            user: User making the request
            max_length: Maximum length of summary

        Returns:
            Dict with summary and metadata
        """
        prompt = f"""Please provide a concise summary of the following content in no more than {max_length} words:

{content}

Summary:"""

        return self.generate_completion(
            prompt=prompt,
            user=user,
            temperature=0.5,
            context={'type': 'summary', 'content_length': len(content)}
        )

    def generate_suggestions(
        self,
        context: str,
        suggestion_type: str,
        user,
        count: int = 3
    ) -> Dict[str, Any]:
        """
        Generate smart suggestions.

        Args:
            context: Context for suggestions
            suggestion_type: Type of suggestions to generate
            user: User making the request
            count: Number of suggestions to generate

        Returns:
            Dict with suggestions and metadata
        """
        prompts = {
            'task': f"Based on this context, suggest {count} relevant tasks:\n{context}\n\nSuggested tasks:",
            'reply': f"Suggest {count} appropriate replies to this message:\n{context}\n\nSuggested replies:",
            'tag': f"Suggest {count} relevant tags for this content:\n{context}\n\nSuggested tags:",
            'priority': f"Analyze this and suggest a priority level (Low/Medium/High/Critical):\n{context}\n\nSuggested priority:",
        }

        prompt = prompts.get(suggestion_type, f"Generate {count} suggestions for:\n{context}")

        return self.generate_completion(
            prompt=prompt,
            user=user,
            temperature=0.8,
            context={'type': 'suggestion', 'suggestion_type': suggestion_type}
        )

    def analyze_content(
        self,
        content: str,
        analysis_type: str,
        user
    ) -> Dict[str, Any]:
        """
        Analyze content.

        Args:
            content: Content to analyze
            analysis_type: Type of analysis
            user: User making the request

        Returns:
            Dict with analysis results
        """
        prompts = {
            'sentiment': f"Analyze the sentiment of this text (Positive/Negative/Neutral):\n{content}\n\nSentiment:",
            'keywords': f"Extract key keywords and phrases from this text:\n{content}\n\nKeywords:",
            'summary': f"Provide a detailed analysis of this content:\n{content}\n\nAnalysis:",
        }

        prompt = prompts.get(analysis_type, f"Analyze this content:\n{content}")

        return self.generate_completion(
            prompt=prompt,
            user=user,
            temperature=0.3,
            context={'type': 'analysis', 'analysis_type': analysis_type}
        )

    def translate_content(
        self,
        content: str,
        target_language: str,
        user
    ) -> Dict[str, Any]:
        """
        Translate content to target language.

        Args:
            content: Content to translate
            target_language: Target language code
            user: User making the request

        Returns:
            Dict with translation
        """
        prompt = f"Translate the following text to {target_language}:\n\n{content}\n\nTranslation:"

        return self.generate_completion(
            prompt=prompt,
            user=user,
            temperature=0.3,
            context={'type': 'translation', 'target_language': target_language}
        )

    def review_code(
        self,
        code: str,
        language: str,
        user
    ) -> Dict[str, Any]:
        """
        Review code and provide suggestions.

        Args:
            code: Code to review
            language: Programming language
            user: User making the request

        Returns:
            Dict with review results
        """
        prompt = f"""Review this {language} code and provide:
1. Potential bugs or issues
2. Performance improvements
3. Best practice suggestions
4. Security concerns

Code:
```{language}
{code}
```

Code Review:"""

        return self.generate_completion(
            prompt=prompt,
            user=user,
            temperature=0.5,
            max_tokens=2000,
            context={'type': 'code_review', 'language': language}
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        user
    ) -> Dict[str, Any]:
        """
        Multi-turn chat conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'
            user: User making the request

        Returns:
            Dict with response
        """
        # Build conversation context
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])

        prompt = f"{conversation}\nAssistant:"

        return self.generate_completion(
            prompt=prompt,
            user=user,
            temperature=0.9,
            context={'type': 'chat', 'message_count': len(messages)}
        )


def get_gemini_service(workspace=None, api_key: Optional[str] = None) -> GeminiService:
    """
    Get Gemini service instance.

    Args:
        workspace: Workspace object (optional)
        api_key: API key override (optional)

    Returns:
        GeminiService instance
    """
    return GeminiService(workspace=workspace, api_key=api_key)
