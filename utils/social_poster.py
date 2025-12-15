"""
Social Media Poster Module
Integrates with MCP Social Media Manager for instant and scheduled posting
"""

from datetime import datetime
from typing import Dict, List, Optional, Literal
import streamlit as st


class SocialMediaPoster:
    """
    Handles social media posting via MCP Social Media Manager extension
    Supports instant and scheduled posting to multiple platforms
    """
    
    SUPPORTED_PLATFORMS = ["linkedin", "twitter", "instagram", "facebook"]
    
    def __init__(self):
        """Initialize the social media poster"""
        self.posting_history: List[Dict] = []
    
    def validate_platform(self, platform: str) -> bool:
        """
        Check if platform is supported
        
        Args:
            platform: Platform name
            
        Returns:
            bool: True if supported
        """
        return platform.lower() in self.SUPPORTED_PLATFORMS
    
    def post_instant(
        self, 
        platform: str, 
        content: str, 
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Post content immediately to a platform
        
        Args:
            platform: Target platform (linkedin, twitter, instagram, facebook)
            content: Post content/caption
            media_urls: Optional list of image/video URLs
            
        Returns:
            Dict with status and message
        """
        try:
            if not self.validate_platform(platform):
                return {
                    "success": False,
                    "message": f"Platform '{platform}' is not supported"
                }
            
            # TODO: Integrate with MCP Social Media Manager tool
            # This is a placeholder that simulates the MCP call
            # In production, this would call the actual MCP extension
            
            post_data = {
                "platform": platform.lower(),
                "content": content,
                "media": media_urls or [],
                "timestamp": datetime.now().isoformat(),
                "type": "instant"
            }
            
            # Simulate successful post
            self.posting_history.append(post_data)
            
            return {
                "success": True,
                "message": f"Successfully posted to {platform.title()}!",
                "post_id": f"{platform}_{len(self.posting_history)}",
                "timestamp": post_data["timestamp"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error posting to {platform}: {str(e)}"
            }
    
    def schedule_post(
        self,
        platform: str,
        content: str,
        scheduled_time: datetime,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Schedule content for future posting
        
        Args:
            platform: Target platform
            content: Post content
            scheduled_time: When to post (datetime object)
            media_urls: Optional media URLs
            
        Returns:
            Dict with status and message
        """
        try:
            if not self.validate_platform(platform):
                return {
                    "success": False,
                    "message": f"Platform '{platform}' is not supported"
                }
            
            # Validate scheduled time is in the future
            if scheduled_time <= datetime.now():
                return {
                    "success": False,
                    "message": "Scheduled time must be in the future"
                }
            
            # TODO: Integrate with MCP Social Media Manager scheduling API
            # This is a placeholder that simulates the MCP call
            
            schedule_data = {
                "platform": platform.lower(),
                "content": content,
                "media": media_urls or [],
                "scheduled_for": scheduled_time.isoformat(),
                "created_at": datetime.now().isoformat(),
                "type": "scheduled",
                "status": "pending"
            }
            
            # Simulate successful scheduling
            self.posting_history.append(schedule_data)
            
            return {
                "success": True,
                "message": f"Successfully scheduled post for {platform.title()} at {scheduled_time.strftime('%Y-%m-%d %H:%M')}",
                "schedule_id": f"sched_{platform}_{len(self.posting_history)}",
                "scheduled_for": schedule_data["scheduled_for"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error scheduling post for {platform}: {str(e)}"
            }
    
    def post_to_multiple(
        self,
        platforms: List[str],
        content_dict: Dict[str, str],
        mode: Literal["instant", "scheduled"] = "instant",
        scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Dict]:
        """
        Post to multiple platforms at once
        
        Args:
            platforms: List of platform names
            content_dict: Dictionary mapping platform -> content
            mode: "instant" or "scheduled"
            scheduled_time: Required if mode is "scheduled"
            
        Returns:
            Dict mapping platform -> result
        """
        results = {}
        
        for platform in platforms:
            if platform not in content_dict:
                results[platform] = {
                    "success": False,
                    "message": f"No content provided for {platform}"
                }
                continue
            
            content = content_dict[platform]
            
            if mode == "instant":
                results[platform] = self.post_instant(platform, content)
            elif mode == "scheduled":
                if not scheduled_time:
                    results[platform] = {
                        "success": False,
                        "message": "Scheduled time is required for scheduled posts"
                    }
                else:
                    results[platform] = self.schedule_post(
                        platform, content, scheduled_time
                    )
        
        return results
    
    def get_posting_history(self) -> List[Dict]:
        """
        Get history of all posts
        
        Returns:
            List of post records
        """
        return self.posting_history
    
    def get_scheduled_posts(self) -> List[Dict]:
        """
        Get only scheduled posts
        
        Returns:
            List of scheduled post records
        """
        return [
            post for post in self.posting_history 
            if post.get("type") == "scheduled" and post.get("status") == "pending"
        ]


def display_posting_ui(
    poster: SocialMediaPoster,
    generated_content: Dict[str, str],
    selected_platforms: List[str]
):
    """
    Display posting UI in Streamlit
    
    Args:
        poster: SocialMediaPoster instance
        generated_content: Dict mapping platform -> content
        selected_platforms: List of platforms to post to
    """
    st.subheader("📤 Post to Social Media")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Post Instantly", type="primary", use_container_width=True):
            with st.spinner("Posting to platforms..."):
                results = poster.post_to_multiple(
                    selected_platforms,
                    generated_content,
                    mode="instant"
                )
                
                # Display results
                for platform, result in results.items():
                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
    
    with col2:
        with st.expander("📅 Schedule Post"):
            schedule_date = st.date_input("Select Date")
            schedule_time = st.time_input("Select Time")
            
            if st.button("Schedule", use_container_width=True):
                # Combine date and time
                scheduled_datetime = datetime.combine(schedule_date, schedule_time)
                
                with st.spinner("Scheduling posts..."):
                    results = poster.post_to_multiple(
                        selected_platforms,
                        generated_content,
                        mode="scheduled",
                        scheduled_time=scheduled_datetime
                    )
                    
                    # Display results
                    for platform, result in results.items():
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
    
    # Display posting history
    if poster.get_posting_history():
        with st.expander("📊 View Posting History"):
            history = poster.get_posting_history()
            for i, post in enumerate(reversed(history[-10:])):  # Show last 10
                st.markdown(f"""
                **{post['platform'].title()}** - {post['type'].title()}  
                {post.get('timestamp') or post.get('created_at')}  
                Status: {post.get('status', 'posted')}
                """)
                if i < len(history) - 1:
                    st.divider()
