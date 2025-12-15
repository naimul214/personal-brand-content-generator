"""
Personal Brand Content Generator
Main Streamlit Application

A GenAI-powered tool that transforms long-form content into platform-specific social media posts
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm_orchestrator import ContentGenerator
from src.prompts import get_supported_platforms
from utils.config import Config
from utils.social_poster import SocialMediaPoster, display_posting_ui
from utils.formatters import (
    format_for_download,
    format_for_csv,
    format_for_json,
    clean_content_for_platform,
    prepare_for_posting
)


# Page Configuration
st.set_page_config(
    page_title="Personal Brand Content Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
    }
    .platform-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        color: #000000;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = {}
    if "content_generator" not in st.session_state:
        st.session_state.content_generator = None
    if "social_poster" not in st.session_state:
        st.session_state.social_poster = SocialMediaPoster()
    if "generation_count" not in st.session_state:
        st.session_state.generation_count = 0


def render_sidebar():
    """Render the sidebar with configuration options"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key Configuration
        with st.expander("🔑 API Keys", expanded=False):
            api_key_option = st.radio(
                "API Key Source",
                ["Use .env file", "Enter manually"],
                help="Choose whether to use keys from .env or enter them here"
            )
            
            if api_key_option == "Enter manually":
                llm_provider = st.selectbox(
                    "LLM Provider",
                    ["openai", "anthropic"],
                    index=0
                )
                
                if llm_provider == "openai":
                    manual_key = st.text_input("OpenAI API Key", type="password")
                    if manual_key:
                        os.environ["OPENAI_API_KEY"] = manual_key
                        Config.OPENAI_API_KEY = manual_key
                else:
                    manual_key = st.text_input("Anthropic API Key", type="password")
                    if manual_key:
                        os.environ["ANTHROPIC_API_KEY"] = manual_key
                        Config.ANTHROPIC_API_KEY = manual_key
                
                Config.DEFAULT_LLM_PROVIDER = llm_provider
        
        # Validate configuration
        is_valid, error_msg = Config.validate()
        
        if is_valid:
            st.success("✅ Configuration valid")
        else:
            st.error(f"❌ {error_msg}")
            st.info("💡 Add your API key in .env file or enter it manually above")
        
        st.divider()
        
        # Platform Selection
        st.markdown("### 📱 Target Platforms")
        platforms = get_supported_platforms()
        
        selected_platforms = []
        for platform in platforms:
            platform_icons = {
                "linkedin": "💼",
                "twitter": "🐦",
                "instagram": "📸",
                "facebook": "👥"
            }
            
            if st.checkbox(
                f"{platform_icons.get(platform, '📱')} {platform.title()}",
                value=True,
                key=f"platform_{platform}"
            ):
                selected_platforms.append(platform)
        
        st.divider()
        
        # Tone Selection
        st.markdown("### 🎨 Content Tone")
        tone = st.select_slider(
            "Select tone",
            options=["Formal", "Professional", "Casual"],
            value="Professional",
            help="Adjust the tone of generated content"
        )
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Statistics")
        st.metric("Generated Posts", st.session_state.generation_count)
        st.metric("Selected Platforms", len(selected_platforms))
        
        return selected_platforms, tone.lower(), is_valid


def render_main_content(selected_platforms, tone, config_valid):
    """Render the main content area"""
    
    # Header
    st.markdown('<p class="main-header">🚀 Personal Brand Content Generator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Transform long-form content into platform-specific social media posts using AI</p>',
        unsafe_allow_html=True
    )
    
    # Check configuration
    if not config_valid:
        st.error("⚠️ Please configure your API keys in the sidebar before generating content.")
        return
    
    if not selected_platforms:
        st.warning("⚠️ Please select at least one platform in the sidebar.")
        return
    
    # Source Content Input
    st.markdown("### 📝 Source Content")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        source_content = st.text_area(
            "Paste your long-form content here",
            height=300,
            placeholder="Enter your blog post, article, newsletter, or any long-form content here...",
            help="Minimum 50 characters required"
        )
    
    with col2:
        st.markdown("**Quick Tips:**")
        st.info("""
        ✅ Use blog posts or articles
        ✅ Min 50 characters
        ✅ More content = better results
        
        📌 Sample content available in `examples/` folder
        """)
        
        # Load sample content button
        if st.button("📄 Load Sample Content", use_container_width=True):
            try:
                with open("examples/sample_content.txt", "r", encoding="utf-8") as f:
                    sample = f.read()
                    st.session_state.sample_content = sample
                    st.rerun()
            except:
                st.error("Sample file not found")
    
    # Use sample content if loaded
    if "sample_content" in st.session_state and not source_content:
        source_content = st.session_state.sample_content
        st.text_area("Loaded sample content", value=source_content, height=300, disabled=True, key="sample_display")
    
    # Character count
    if source_content:
        char_count = len(source_content)
        st.caption(f"Character count: {char_count}")
    
    # Generate Button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_button = st.button(
            "✨ Generate Content",
            type="primary",
            use_container_width=True,
            disabled=not source_content or len(source_content.strip()) < 50
        )
    
    # Generation Logic
    if generate_button:
        if not st.session_state.content_generator:
            try:
                st.session_state.content_generator = ContentGenerator()
            except Exception as e:
                st.error(f"Failed to initialize content generator: {str(e)}")
                return
        
        with st.spinner("🤖 Generating platform-specific content..."):
            generator = st.session_state.content_generator
            
            # Generate content for all selected platforms
            results = generator.generate_for_multiple_platforms(
                source_content,
                selected_platforms,
                tone
            )
            
            # Store results and clean content
            st.session_state.generated_content = {}
            st.session_state.last_source_content = source_content  # Store for regeneration
            
            for platform, result in results.items():
                if result["success"]:
                    # Clean and prepare content for the platform
                    cleaned_content = clean_content_for_platform(result["content"], platform)
                    st.session_state.generated_content[platform] = cleaned_content
            
            st.session_state.generation_count += len(selected_platforms)
            
            # Show success message
            if st.session_state.generated_content:
                st.success(f"✅ Successfully generated content for {len(st.session_state.generated_content)} platforms!")
    
    # Display Generated Content
    if st.session_state.generated_content:
        st.markdown("---")
        st.markdown("### 📊 Generated Content")
        
        # Create tabs for each platform
        tabs = st.tabs([f"{platform.title()} {get_platform_icon(platform)}" 
                       for platform in st.session_state.generated_content.keys()])
        
        for idx, (platform, content) in enumerate(st.session_state.generated_content.items()):
            with tabs[idx]:
                render_platform_tab(platform, content)
        
        st.markdown("---")
        
        # Posting Section
        if st.session_state.generated_content:
            display_posting_ui(
                st.session_state.social_poster,
                st.session_state.generated_content,
                list(st.session_state.generated_content.keys())
            )
            
            # Download Options
            st.markdown("---")
            st.markdown("### 📥 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download as TXT
                download_content = format_for_download(
                    st.session_state.generated_content,
                    metadata={
                        "Platforms": ", ".join(st.session_state.generated_content.keys()),
                        "Generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
                st.download_button(
                    label="📄 Download as TXT",
                    data=download_content,
                    file_name=f"social_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                # Download as CSV
                csv_content = format_for_csv(st.session_state.generated_content)
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_content,
                    file_name=f"social_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                # Download as JSON
                json_content = format_for_json(
                    st.session_state.generated_content,
                    metadata={
                        "generated_by": "Personal Brand Content Generator",
                        "version": "1.0"
                    }
                )
                st.download_button(
                    label="📋 Download as JSON",
                    data=json_content,
                    file_name=f"social_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )


def get_platform_icon(platform: str) -> str:
    """Get emoji icon for platform"""
    icons = {
        "linkedin": "💼",
        "twitter": "🐦",
        "instagram": "📸",
        "facebook": "👥"
    }
    return icons.get(platform.lower(), "📱")


def render_platform_tab(platform: str, content: str):
    """Render content for a specific platform tab"""
    
    # Display content in a styled container with proper text color
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; 
                    color: #1f1f1f; border: 1px solid #dee2e6; white-space: pre-wrap; 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            {content.replace(chr(10), "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Platform stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Characters", len(content))
    
    with col2:
        char_limit = Config.get_platform_limit(platform)
        st.metric("Limit", f"{char_limit:,}")
    
    with col3:
        within_limit = len(content) <= char_limit or platform.lower() == "twitter"
        status = "✅ Good" if within_limit else "⚠️ Over"
        st.metric("Status", status)
    
    # Copy button
    st.text_area(
        f"Copy {platform.title()} content",
        value=content,
        height=200,
        key=f"copy_{platform}",
        help="Select all (Ctrl+A) and copy (Ctrl+C)"
    )
    
    # Regenerate option
    with st.expander("🔄 Regenerate with feedback"):
        feedback = st.text_input(
            "What would you like to change?",
            key=f"feedback_{platform}",
            placeholder="E.g., Make it more casual, add more emojis, focus on X topic..."
        )
        
        if st.button(f"Regenerate {platform.title()}", key=f"regen_{platform}"):
            if feedback:
                with st.spinner("Regenerating..."):
                    generator = st.session_state.content_generator
                    result = generator.regenerate_content(
                        st.session_state.get("last_source_content", ""),
                        platform,
                        feedback,
                        content
                    )
                    
                    if result["success"]:
                        st.session_state.generated_content[platform] = result["content"]
                        st.success("✅ Content regenerated!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please provide feedback for regeneration")


def generate_download_text(content_dict: dict) -> str:
    """Generate formatted text file content for download"""
    
    output = f"""
{'='*60}
PERSONAL BRAND CONTENT GENERATOR
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

"""
    
    for platform, content in content_dict.items():
        output += f"""
{'='*60}
{platform.upper()}
{'='*60}

{content}

"""
    
    return output


def main():
    """Main application entry point"""
    initialize_session_state()
    selected_platforms, tone, config_valid = render_sidebar()
    render_main_content(selected_platforms, tone, config_valid)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Built with ❤️ using Streamlit, LangChain, and OpenAI/Anthropic | COSC41000 Final Project</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
