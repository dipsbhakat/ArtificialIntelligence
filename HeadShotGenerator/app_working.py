import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Tuple


class WorkingHeadshotGenerator:
    """Working professional headshot generator with reliable enhancements"""
    
    def professional_crop(self, image: Image.Image, style: str = "headshot") -> Image.Image:
        """Apply professional cropping based on portrait photography standards"""
        width, height = image.size
        
        if style == "headshot":
            # Professional headshot: 4:5 ratio (portrait)
            target_ratio = 4/5
            
            if width/height > target_ratio:
                # Image is too wide - crop from sides
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                image = image.crop((left, 0, left + new_width, height))
            else:
                # Image is too tall - crop from top/bottom, keep face area
                new_height = int(width / target_ratio)
                # Position to keep upper portion (where face typically is)
                top = int(height * 0.1)  # Start 10% from top
                if top + new_height > height:
                    top = height - new_height
                image = image.crop((0, top, width, top + new_height))
                
        elif style == "corporate":
            # Corporate style: 3:4 ratio (more shoulder area)
            target_ratio = 3/4
            
            if width/height > target_ratio:
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                image = image.crop((left, 0, left + new_width, height))
            else:
                new_height = int(width / target_ratio)
                top = int(height * 0.05)  # Less aggressive top crop
                if top + new_height > height:
                    top = height - new_height
                image = image.crop((0, top, width, top + new_height))
        
        return image
    
    def professional_enhancement(self, image: Image.Image, 
                               brightness: float = 1.1,
                               contrast: float = 1.15,
                               saturation: float = 1.05,
                               warmth: float = 1.02) -> Image.Image:
        """Apply professional image enhancements"""
        
        # Brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
        
        # Contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # Saturation adjustment
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)
        
        # Warmth adjustment (subtle color temperature shift)
        if warmth != 1.0:
            r, g, b = image.split()
            # Slightly enhance red channel for warmth
            enhancer = ImageEnhance.Brightness(r)
            r = enhancer.enhance(warmth)
            # Slightly reduce blue for warmth
            enhancer = ImageEnhance.Brightness(b)
            b = enhancer.enhance(2.0 - warmth)
            image = Image.merge('RGB', (r, g, b))
        
        return image
    
    def professional_sharpening(self, image: Image.Image) -> Image.Image:
        """Apply professional-grade sharpening"""
        # High-quality unsharp mask
        sharpened = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
        return sharpened
    
    def skin_smoothing(self, image: Image.Image, intensity: float = 0.3) -> Image.Image:
        """Apply subtle skin smoothing"""
        if intensity <= 0:
            return image
            
        # Create a slightly blurred version
        blurred = image.filter(ImageFilter.GaussianBlur(radius=1.2))
        
        # Blend original with blurred version
        # Use a low intensity to maintain natural look
        smoothed = Image.blend(image, blurred, intensity * 0.4)
        
        return smoothed
    
    def create_professional_background(self, image: Image.Image, bg_style: str = "studio_gray") -> Image.Image:
        """Create professional background (simplified version)"""
        if bg_style == "original":
            return image
            
        width, height = image.size
        
        # Create background
        if bg_style == "studio_gray":
            background = Image.new('RGB', (width, height), (240, 240, 245))
        elif bg_style == "executive_blue":
            background = Image.new('RGB', (width, height), (45, 55, 72))
        elif bg_style == "corporate_white":
            background = Image.new('RGB', (width, height), (255, 255, 255))
        elif bg_style == "warm_beige":
            background = Image.new('RGB', (width, height), (245, 240, 235))
        else:
            return image
        
        # For now, return original image (in a full implementation, this would use background removal)
        return image
    
    def resize_professional(self, image: Image.Image, size: Tuple[int, int] = (512, 512)) -> Image.Image:
        """Resize with professional quality"""
        # High-quality resize
        resized = image.resize(size, Image.Resampling.LANCZOS)
        
        # Subtle sharpening after resize
        resized = resized.filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=1))
        
        return resized


def main():
    st.set_page_config(
        page_title="Professional Headshot Generator",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header"><h1>📸 Professional Headshot Generator</h1><p>Create studio-quality professional headshots</p></div>', unsafe_allow_html=True)
    
    # Initialize generator
    generator = WorkingHeadshotGenerator()
    
    # Sidebar
    st.sidebar.header("🎨 Professional Settings")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload Your Photo",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear, well-lit photo for best results"
    )
    
    if uploaded_file is not None:
        # Load image
        original_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original Photo")
            st.image(original_image, use_column_width=True)
        
        # Settings
        st.sidebar.subheader("🎭 Style Settings")
        
        crop_style = st.sidebar.selectbox(
            "Crop Style",
            ["headshot", "corporate"],
            help="Headshot: Close portrait. Corporate: More shoulder area"
        )
        
        bg_style = st.sidebar.selectbox(
            "Background",
            ["original", "studio_gray", "executive_blue", "corporate_white", "warm_beige"]
        )
        
        st.sidebar.subheader("✨ Enhancement")
        
        brightness = st.sidebar.slider("Brightness", 0.8, 1.4, 1.1, 0.05)
        contrast = st.sidebar.slider("Contrast", 0.8, 1.6, 1.15, 0.05)
        saturation = st.sidebar.slider("Saturation", 0.8, 1.3, 1.05, 0.05)
        warmth = st.sidebar.slider("Warmth", 0.95, 1.15, 1.02, 0.01)
        
        st.sidebar.subheader("🎯 Effects")
        
        skin_smooth = st.sidebar.slider("Skin Smoothing", 0.0, 0.8, 0.3, 0.1)
        
        st.sidebar.subheader("📐 Output")
        
        output_size = st.sidebar.selectbox(
            "Size",
            [
                "512x512 (Professional)",
                "400x400 (LinkedIn)", 
                "600x600 (High-res)",
                "800x800 (Premium)"
            ]
        )
        
        size_map = {
            "512x512 (Professional)": (512, 512),
            "400x400 (LinkedIn)": (400, 400),
            "600x600 (High-res)": (600, 600),
            "800x800 (Premium)": (800, 800)
        }
        size = size_map[output_size]
        
        # Process button
        if st.sidebar.button("🎨 Generate Professional Headshot", type="primary"):
            with st.spinner("Creating professional headshot..."):
                # Processing pipeline
                processed_image = original_image.copy()
                
                # Professional cropping
                processed_image = generator.professional_crop(processed_image, crop_style)
                
                # Skin smoothing
                if skin_smooth > 0:
                    processed_image = generator.skin_smoothing(processed_image, skin_smooth)
                
                # Professional enhancement
                processed_image = generator.professional_enhancement(
                    processed_image, brightness, contrast, saturation, warmth
                )
                
                # Background (simplified)
                processed_image = generator.create_professional_background(processed_image, bg_style)
                
                # Professional sharpening
                processed_image = generator.professional_sharpening(processed_image)
                
                # Final resize
                final_image = generator.resize_professional(processed_image, size)
                
                # Display result
                with col2:
                    st.subheader("⭐ Professional Result")
                    st.image(final_image, use_column_width=True)
                    
                    # Download
                    buf = io.BytesIO()
                    final_image.save(buf, format="PNG", quality=95)
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="💾 Download Professional Headshot",
                        data=byte_im,
                        file_name=f"professional_headshot_{size[0]}x{size[1]}.png",
                        mime="image/png",
                        type="primary"
                    )
                    
                    st.success(f"✅ Professional headshot created: {size[0]}×{size[1]} pixels")
        
        # Tips
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 Pro Tips")
        st.sidebar.markdown("""
        **📸 Best Results:**
        - Use natural lighting
        - Face the light source
        - Maintain good posture
        - Wear solid colors
        - Look directly at camera
        """)
    
    else:
        st.info("👆 Upload a photo to create your professional headshot")
        
        # Features
        st.subheader("🌟 Professional Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 Professional Cropping**
            - Portrait photography ratios
            - Headshot and corporate styles
            - Optimal face positioning
            """)
        
        with col2:
            st.markdown("""
            **✨ Studio Enhancement**
            - Professional color grading
            - Skin smoothing
            - Advanced sharpening
            """)
        
        with col3:
            st.markdown("""
            **📐 Quality Output**
            - Multiple professional sizes
            - High-quality processing
            - Studio-grade results
            """)


if __name__ == "__main__":
    main()
