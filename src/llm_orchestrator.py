"""
LLM Orchestrator Module
Handles content generation using LangChain and LLM APIs
"""

from typing import Dict, Optional, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from utils.config import Config
from src.prompts import get_platform_prompt, get_supported_platforms, get_platform_limit


class ContentGenerator:
    """
    Orchestrates content generation for multiple social media platforms using LangChain
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize the content generator
        
        Args:
            llm_provider: Optional LLM provider override ("openai" or "anthropic")
        """
        try:
            self.llm = Config.get_llm_client(llm_provider)
            self.provider = llm_provider or Config.DEFAULT_LLM_PROVIDER
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM client: {str(e)}")
    
    def generate_content(
        self,
        source_content: str,
        platform: str,
        tone: str = "professional"
    ) -> Dict[str, any]:
        """
        Generate platform-specific content from source material
        
        Args:
            source_content: Original long-form content to transform
            platform: Target platform (linkedin, twitter, instagram, facebook)
            tone: Tone adjustment ("professional", "casual", "formal")
            
        Returns:
            Dict with generated content and metadata
        """
        try:
            # Validate platform
            if platform.lower() not in get_supported_platforms():
                return {
                    "success": False,
                    "error": f"Platform '{platform}' is not supported",
                    "content": None
                }
            
            # Validate source content
            if not source_content or len(source_content.strip()) < 50:
                return {
                    "success": False,
                    "error": "Source content is too short. Please provide at least 50 characters.",
                    "content": None
                }
            
            # Get platform-specific prompt
            system_prompt = get_platform_prompt(platform)
            
            # Add tone guidance if specified
            tone_guidance = ""
            if tone.lower() == "casual":
                tone_guidance = "\n\nTone: Use a slightly more casual and relaxed approach."
            elif tone.lower() == "formal":
                tone_guidance = "\n\nTone: Use a more formal and authoritative voice."
            
            # Construct messages for LangChain
            messages = [
                SystemMessage(content=system_prompt + tone_guidance),
                HumanMessage(content=f"Transform this content:\n\n{source_content}")
            ]
            
            # Generate content using LLM
            response = self.llm.invoke(messages)
            generated_content = response.content.strip()
            
            # Validate output length
            char_limit = get_platform_limit(platform)
            is_within_limit = True
            
            # Special handling for Twitter (thread format)
            if platform.lower() == "twitter":
                # Count tweets in thread (look for numbered tweets or line breaks)
                tweets = [t.strip() for t in generated_content.split("\n\n") if t.strip()]
                is_within_limit = all(len(tweet) <= 280 for tweet in tweets)
            else:
                is_within_limit = len(generated_content) <= char_limit
            
            return {
                "success": True,
                "content": generated_content,
                "platform": platform,
                "char_count": len(generated_content),
                "char_limit": char_limit,
                "within_limit": is_within_limit,
                "provider": self.provider
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating content: {str(e)}",
                "content": None
            }
    
    def generate_for_multiple_platforms(
        self,
        source_content: str,
        platforms: list,
        tone: str = "professional"
    ) -> Dict[str, Dict]:
        """
        Generate content for multiple platforms at once
        
        Args:
            source_content: Original content to transform
            platforms: List of target platforms
            tone: Tone to use for all platforms
            
        Returns:
            Dict mapping platform -> generation result
        """
        results = {}
        
        for platform in platforms:
            result = self.generate_content(source_content, platform, tone)
            results[platform] = result
        
        return results
    
    def regenerate_content(
        self,
        source_content: str,
        platform: str,
        feedback: str,
        previous_content: str
    ) -> Dict[str, any]:
        """
        Regenerate content with specific feedback
        
        Args:
            source_content: Original source content
            platform: Target platform
            feedback: User feedback on what to improve
            previous_content: Previously generated content
            
        Returns:
            Dict with regenerated content
        """
        try:
            system_prompt = get_platform_prompt(platform)
            
            # Add regeneration context
            regen_message = f"""
Previous version:
{previous_content}

User feedback:
{feedback}

Please regenerate the content incorporating this feedback while maintaining platform requirements.

Original source content:
{source_content}
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=regen_message)
            ]
            
            response = self.llm.invoke(messages)
            generated_content = response.content.strip()
            
            return {
                "success": True,
                "content": generated_content,
                "platform": platform,
                "regenerated": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error regenerating content: {str(e)}",
                "content": None
            }
    
    def validate_content_quality(self, content: str, platform: str) -> Dict[str, any]:
        """
        Validate if generated content meets platform requirements
        
        Args:
            content: Generated content to validate
            platform: Target platform
            
        Returns:
            Dict with validation results
        """
        issues = []
        char_limit = get_platform_limit(platform)
        
        # Check character count
        if platform.lower() != "twitter":
            if len(content) > char_limit:
                issues.append(f"Content exceeds {char_limit} character limit")
        
        # Platform-specific checks
        if platform.lower() == "linkedin":
            if "#" not in content:
                issues.append("Missing hashtags")
            if "?" not in content:
                issues.append("Consider adding a call-to-action question")
        
        elif platform.lower() == "twitter":
            tweets = [t.strip() for t in content.split("\n\n") if t.strip()]
            if len(tweets) < 3:
                issues.append("Thread should have at least 3 tweets")
            for i, tweet in enumerate(tweets):
                if len(tweet) > 280:
                    issues.append(f"Tweet {i+1} exceeds 280 characters")
        
        elif platform.lower() == "instagram":
            if "#" not in content:
                issues.append("Missing hashtags")
            hashtag_count = content.count("#")
            if hashtag_count < 10:
                issues.append(f"Only {hashtag_count} hashtags found. Aim for 20-30.")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "char_count": len(content)
        }


def create_generator(llm_provider: Optional[str] = None) -> ContentGenerator:
    """
    Factory function to create a ContentGenerator instance
    
    Args:
        llm_provider: Optional LLM provider
        
    Returns:
        ContentGenerator instance
    """
    return ContentGenerator(llm_provider)
