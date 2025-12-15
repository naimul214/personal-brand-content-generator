"""
Configuration Module
Handles environment variables and LLM client initialization
"""

import os
from dotenv import load_dotenv
from typing import Optional, Literal

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the application"""
    
    # LLM Provider Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    # Platform Character Limits
    LINKEDIN_CHAR_LIMIT: int = int(os.getenv("LINKEDIN_CHAR_LIMIT", "3000"))
    TWITTER_CHAR_LIMIT: int = int(os.getenv("TWITTER_CHAR_LIMIT", "280"))
    INSTAGRAM_CHAR_LIMIT: int = int(os.getenv("INSTAGRAM_CHAR_LIMIT", "2200"))
    FACEBOOK_CHAR_LIMIT: int = int(os.getenv("FACEBOOK_CHAR_LIMIT", "63206"))
    
    # Timezone
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """
        Validate configuration settings
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if cls.DEFAULT_LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            return False, "OpenAI API key is missing. Please set OPENAI_API_KEY in .env"
        
        if cls.DEFAULT_LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            return False, "Anthropic API key is missing. Please set ANTHROPIC_API_KEY in .env"
        
        if cls.DEFAULT_LLM_PROVIDER not in ["openai", "anthropic"]:
            return False, f"Invalid LLM provider: {cls.DEFAULT_LLM_PROVIDER}. Must be 'openai' or 'anthropic'"
        
        return True, ""
    
    @classmethod
    def get_llm_client(cls, provider: Optional[str] = None):
        """
        Initialize and return the appropriate LLM client
        
        Args:
            provider: Optional provider override ("openai" or "anthropic")
            
        Returns:
            Initialized LLM client object
            
        Raises:
            ValueError: If provider is invalid or API key is missing
        """
        selected_provider = provider or cls.DEFAULT_LLM_PROVIDER
        
        if selected_provider == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-5-mini",
                temperature=0.7,
                api_key=cls.OPENAI_API_KEY
            )
        
        elif selected_provider == "anthropic":
            if not cls.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not configured")
            
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model="claude-3-5-haiku-20241022",
                temperature=0.7,
                api_key=cls.ANTHROPIC_API_KEY
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {selected_provider}")
    
    @classmethod
    def get_platform_limit(cls, platform: str) -> int:
        """
        Get character limit for a specific platform
        
        Args:
            platform: Platform name (linkedin, twitter, instagram, facebook)
            
        Returns:
            Character limit for the platform
        """
        platform_lower = platform.lower()
        
        limits = {
            "linkedin": cls.LINKEDIN_CHAR_LIMIT,
            "twitter": cls.TWITTER_CHAR_LIMIT,
            "instagram": cls.INSTAGRAM_CHAR_LIMIT,
            "facebook": cls.FACEBOOK_CHAR_LIMIT
        }
        
        return limits.get(platform_lower, 1000)


# Convenience function for quick access
def get_config() -> Config:
    """Get the configuration singleton"""
    return Config
