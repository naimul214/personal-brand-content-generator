"""
Content Formatting Utilities
Handles content cleaning, formatting, and export operations
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


def clean_markdown_formatting(text: str) -> str:
    """
    Remove markdown formatting from text
    
    Args:
        text: Text with potential markdown formatting
        
    Returns:
        Cleaned text without markdown syntax
    """
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove headers (# Header)
    text = re.sub(r'#+\s+', '', text)
    
    # Remove links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove inline code `code`
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    return text


def clean_for_twitter(text: str) -> str:
    """
    Clean and format text specifically for Twitter
    Remove bold markdown but keep emojis and hashtags
    
    Args:
        text: Text to clean
        
    Returns:
        Twitter-ready text
    """
    # Remove bold markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove extra whitespace but preserve single line breaks
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    return '\n\n'.join(cleaned_lines)


def clean_for_linkedin(text: str) -> str:
    """
    Format text for LinkedIn (preserves some formatting)
    
    Args:
        text: Text to format
        
    Returns:
        LinkedIn-ready text
    """
    # LinkedIn supports some basic formatting, but clean bold markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # Ensure proper paragraph spacing
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    return '\n\n'.join(cleaned_lines)


def clean_for_instagram(text: str) -> str:
    """
    Format text for Instagram (keep emojis, hashtags, line breaks)
    
    Args:
        text: Text to format
        
    Returns:
        Instagram-ready text
    """
    # Remove markdown but keep emojis
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Instagram likes line breaks - preserve them
    return text


def clean_for_facebook(text: str) -> str:
    """
    Format text for Facebook
    
    Args:
        text: Text to format
        
    Returns:
        Facebook-ready text
    """
    # Remove markdown formatting
    text = clean_markdown_formatting(text)
    
    # Clean up extra spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def clean_content_for_platform(text: str, platform: str) -> str:
    """
    Apply platform-specific cleaning
    
    Args:
        text: Content to clean
        platform: Target platform
        
    Returns:
        Cleaned content
    """
    platform_lower = platform.lower()
    
    cleaners = {
        'twitter': clean_for_twitter,
        'linkedin': clean_for_linkedin,
        'instagram': clean_for_instagram,
        'facebook': clean_for_facebook
    }
    
    cleaner = cleaners.get(platform_lower, clean_markdown_formatting)
    return cleaner(text)


def truncate_to_limit(text: str, limit: int, add_ellipsis: bool = True) -> str:
    """
    Truncate text to character limit
    
    Args:
        text: Text to truncate
        limit: Character limit
        add_ellipsis: Whether to add "..." at the end
        
    Returns:
        Truncated text
    """
    if len(text) <= limit:
        return text
    
    if add_ellipsis:
        return text[:limit-3] + "..."
    else:
        return text[:limit]


def extract_hashtags(text: str) -> List[str]:
    """
    Extract all hashtags from text
    
    Args:
        text: Text containing hashtags
        
    Returns:
        List of hashtags (without # symbol)
    """
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags


def count_hashtags(text: str) -> int:
    """
    Count number of hashtags in text
    
    Args:
        text: Text to analyze
        
    Returns:
        Number of hashtags
    """
    return len(extract_hashtags(text))


def format_for_download(content_dict: Dict[str, str], metadata: Optional[Dict] = None) -> str:
    """
    Format content dictionary into a downloadable text file
    
    Args:
        content_dict: Dictionary mapping platform -> content
        metadata: Optional metadata to include
        
    Returns:
        Formatted string ready for download
    """
    separator = "=" * 70
    
    # Header
    output = f"""
{separator}
PERSONAL BRAND CONTENT GENERATOR - EXPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{separator}
"""
    
    # Add metadata if provided
    if metadata:
        output += "\n\nMETADATA:\n"
        for key, value in metadata.items():
            output += f"  {key}: {value}\n"
        output += f"\n{separator}\n"
    
    # Add content for each platform
    for platform, content in content_dict.items():
        platform_title = platform.upper()
        char_count = len(content)
        hashtag_count = count_hashtags(content)
        
        output += f"""

{separator}
PLATFORM: {platform_title}
Characters: {char_count}
Hashtags: {hashtag_count}
{separator}

{content}

"""
    
    # Footer
    output += f"""
{separator}
END OF EXPORT
{separator}
"""
    
    return output


def format_for_csv(content_dict: Dict[str, str]) -> str:
    """
    Format content as CSV for spreadsheet import
    
    Args:
        content_dict: Dictionary mapping platform -> content
        
    Returns:
        CSV formatted string
    """
    csv_lines = ["Platform,Content,Character Count,Hashtag Count"]
    
    for platform, content in content_dict.items():
        # Escape quotes and commas in content
        escaped_content = content.replace('"', '""')
        char_count = len(content)
        hashtag_count = count_hashtags(content)
        
        csv_lines.append(f'"{platform}","{escaped_content}",{char_count},{hashtag_count}')
    
    return '\n'.join(csv_lines)


def format_for_json(content_dict: Dict[str, str], metadata: Optional[Dict] = None) -> str:
    """
    Format content as JSON
    
    Args:
        content_dict: Dictionary mapping platform -> content
        metadata: Optional metadata
        
    Returns:
        JSON formatted string
    """
    import json
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "metadata": metadata or {},
        "content": {}
    }
    
    for platform, content in content_dict.items():
        output["content"][platform] = {
            "text": content,
            "char_count": len(content),
            "hashtag_count": count_hashtags(content),
            "hashtags": extract_hashtags(content)
        }
    
    return json.dumps(output, indent=2, ensure_ascii=False)


def split_twitter_thread(text: str) -> List[str]:
    """
    Split text into individual tweets from a thread
    
    Args:
        text: Full thread text
        
    Returns:
        List of individual tweets
    """
    # Split by double newlines or tweet numbers
    tweets = re.split(r'\n\n+', text)
    
    # Clean up each tweet
    cleaned_tweets = []
    for tweet in tweets:
        tweet = tweet.strip()
        # Remove tweet numbering like "1/7" or "Tweet 1:"
        tweet = re.sub(r'^(Tweet\s+)?\d+[/:\.]?\s*', '', tweet, flags=re.IGNORECASE)
        if tweet:
            cleaned_tweets.append(tweet)
    
    return cleaned_tweets


def validate_content_length(text: str, platform: str, limits: Dict[str, int]) -> Dict[str, any]:
    """
    Validate if content meets platform length requirements
    
    Args:
        text: Content to validate
        platform: Target platform
        limits: Dictionary of platform limits
        
    Returns:
        Validation result dictionary
    """
    char_count = len(text)
    limit = limits.get(platform.lower(), 1000)
    
    if platform.lower() == 'twitter':
        # Special handling for Twitter threads
        tweets = split_twitter_thread(text)
        valid = all(len(tweet) <= 280 for tweet in tweets)
        return {
            "valid": valid,
            "char_count": char_count,
            "limit": 280,
            "tweet_count": len(tweets),
            "message": f"Thread has {len(tweets)} tweets" if valid else "Some tweets exceed 280 characters"
        }
    else:
        valid = char_count <= limit
        percentage = (char_count / limit) * 100
        
        return {
            "valid": valid,
            "char_count": char_count,
            "limit": limit,
            "percentage": percentage,
            "message": f"{percentage:.1f}% of limit used" if valid else f"Exceeds limit by {char_count - limit} characters"
        }


def add_line_breaks_for_readability(text: str, max_line_length: int = 60) -> str:
    """
    Add line breaks for better readability (useful for Instagram)
    
    Args:
        text: Text to format
        max_line_length: Approximate max characters per line
        
    Returns:
        Text with added line breaks
    """
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        if len(paragraph) > max_line_length:
            words = paragraph.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= max_line_length:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            formatted_paragraphs.append('\n'.join(lines))
        else:
            formatted_paragraphs.append(paragraph)
    
    return '\n\n'.join(formatted_paragraphs)


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace while preserving intentional formatting
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.split('\n')]
    
    # Remove multiple consecutive blank lines (keep max 1)
    cleaned_lines = []
    prev_blank = False
    
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        cleaned_lines.append(line)
        prev_blank = is_blank
    
    return '\n'.join(cleaned_lines).strip()


def prepare_for_posting(content: str, platform: str) -> str:
    """
    Prepare content for posting (final cleanup)
    
    Args:
        content: Content to prepare
        platform: Target platform
        
    Returns:
        Ready-to-post content
    """
    # Clean for platform
    content = clean_content_for_platform(content, platform)
    
    # Remove extra whitespace
    content = remove_extra_whitespace(content)
    
    return content
