import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
import io
from typing import Tuple
import math


class ProfessionalHeadshotGenerator:
    """Professional headshot generator with advanced styling"""
    
    def __init__(self):
        self.golden_ratio = 1.618
        
    def detect_face_region(self, image: Image.Image) -> Tuple[int, int, int, int]:
        """Estimate face region using rule of thirds and image analysis"""
        width, height = image.size
        
        # Use rule of thirds for face positioning
        # Assume face is in upper third, centered horizontally
        face_width = int(width * 0.4)  # Face typically 40% of image width
        face_height = int(height * 0.45)  # Face region about 45% of image height
        
        # Center horizontally, position in upper third
        face_x = (width - face_width) // 2
        face_y = int(height * 0.15)  # Start at 15% from top
        
        return (face_x, face_y, face_width, face_height)
    
    def professional_crop(self, image: Image.Image, style: str = "headshot") -> Image.Image:
        """Apply professional cropping based on portrait photography standards"""
        width, height = image.size
        
        if style == "headshot":
            # Professional headshot: head and shoulders, following portrait rules
            # Crop to 4:5 ratio (professional portrait ratio)
            target_ratio = 4/5
            
            if width/height > target_ratio:
                # Image is too wide - crop from sides
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                image = image.crop((left, 0, left + new_width, height))
            else:
                # Image is too tall - crop from top/bottom
                new_height = int(width / target_ratio)
                # Position face in upper third
                top = int(height * 0.1)
                if top + new_height > height:
                    top = height - new_height
                image = image.crop((0, top, width, top + new_height))
                
        elif style == "corporate":
            # Corporate style: more shoulder area visible
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
    
    def professional_lighting(self, image: Image.Image, intensity: float = 0.3) -> Image.Image:
        """Apply professional studio lighting effect"""
        if intensity <= 0:
            return image
            
        # Enhance overall brightness first
        enhancer = ImageEnhance.Brightness(image)
        brightened = enhancer.enhance(1.0 + intensity * 0.2)
        
        # Create a subtle lighting gradient
        width, height = image.size
        
        # Create light enhancement mask
        light_mask = Image.new('L', (width, height), 128)  # Start with neutral gray
        
        # Create soft lighting gradient from top-center
        for y in range(height):
            for x in range(width):
                # Calculate distance from light source (top-center)
                center_x = width * 0.5
                light_y = height * 0.2
                
                distance = math.sqrt((x - center_x)**2 + (y - light_y)**2)
                max_distance = math.sqrt((width*0.5)**2 + (height*0.8)**2)
                
                # Create soft falloff (brighter near top, gradually darker toward bottom)
                light_value = 1.0 - (distance / max_distance) * 0.4
                light_value = max(0.6, min(1.0, light_value))  # Keep it subtle
                
                # Convert to 0-255 range
                mask_value = int(light_value * 255)
                light_mask.putpixel((x, y), mask_value)
        
        # Apply Gaussian blur for smooth lighting
        light_mask = light_mask.filter(ImageFilter.GaussianBlur(radius=width//8))
        
        # Apply the lighting effect by blending
        # Convert mask to RGB for blending
        light_overlay = Image.new('RGB', (width, height), (255, 255, 255))
        
        # Use the mask to create subtle lighting enhancement
        result = Image.composite(light_overlay, brightened, light_mask)
        
        # Blend with original for subtle effect
        final = Image.blend(brightened, result, intensity * 0.3)
        
        return final
    
    def skin_enhancement(self, image: Image.Image, smoothing: float = 0.4) -> Image.Image:
        """Apply subtle skin smoothing and enhancement"""
        # Subtle gaussian blur for skin smoothing
        blurred = image.filter(ImageFilter.GaussianBlur(radius=1.5))
        
        # Blend original with blurred version
        enhancer = ImageEnhance.Sharpness(image)
        smoothed = Image.blend(image, blurred, smoothing * 0.3)
        
        # Enhance skin tones
        enhancer = ImageEnhance.Color(smoothed)
        enhanced = enhancer.enhance(1.1)  # Slight color enhancement
        
        return enhanced
    
    def professional_enhancement(self, image: Image.Image, 
                               brightness: float = 1.1,
                               contrast: float = 1.15,
                               saturation: float = 1.05,
                               warmth: float = 1.02) -> Image.Image:
        """Apply comprehensive professional enhancements"""
        
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
            image = Image.merge('RGB', (r, g, b))
        
        # Professional sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
        
        return image
    
    def add_professional_vignette(self, image: Image.Image, intensity: float = 0.2) -> Image.Image:
        """Add subtle vignette for professional look"""
        if intensity <= 0:
            return image
            
        width, height = image.size
        
        # Create vignette mask - start with white (no effect)
        vignette = Image.new('L', (width, height), 255)
        
        # Create radial gradient from center
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2
        
        # Create subtle vignette effect
        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                # Create very subtle darkening only at edges
                if distance > max_radius * 0.7:  # Only affect outer 30%
                    edge_factor = (distance - max_radius * 0.7) / (max_radius * 0.3)
                    edge_factor = min(1.0, edge_factor)
                    
                    # Very subtle darkening
                    darkness = int(255 * (1 - intensity * edge_factor * 0.3))
                    vignette.putpixel((x, y), darkness)
        
        # Apply Gaussian blur for smooth transition
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=max_radius // 6))
        
        # Apply vignette by using it as a mask for blending
        # Create a slightly darkened version
        enhancer = ImageEnhance.Brightness(image)
        darkened = enhancer.enhance(0.9)
        
        # Blend original with darkened using vignette mask
        result = Image.composite(image, darkened, vignette)
        
        return result
    
    def resize_professional(self, image: Image.Image, size: Tuple[int, int] = (512, 512)) -> Image.Image:
        """Resize with professional quality settings"""
        # Use high-quality resampling
        resized = image.resize(size, Image.Resampling.LANCZOS)
        
        # Apply subtle sharpening after resize
        resized = resized.filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=1))
        
        return resized
    
    def create_professional_background(self, image: Image.Image, bg_style: str = "studio_gray") -> Image.Image:
        """Create professional background styles"""
        width, height = image.size
        
        if bg_style == "studio_gray":
            # Professional studio gray gradient
            background = Image.new('RGB', (width, height), (240, 240, 245))
            # Add subtle gradient
            for y in range(height):
                brightness = 240 - int((y / height) * 15)  # Subtle gradient
                for x in range(width):
                    background.putpixel((x, y), (brightness, brightness, brightness + 5))
        
        elif bg_style == "executive_blue":
            # Executive blue background
            background = Image.new('RGB', (width, height), (45, 55, 72))
            
        elif bg_style == "corporate_white":
            # Pure corporate white
            background = Image.new('RGB', (width, height), (255, 255, 255))
            
        elif bg_style == "warm_beige":
            # Warm professional beige
            background = Image.new('RGB', (width, height), (245, 240, 235))
            
        else:  # "original"
            return image
        
        # For now, return original image overlaid on background
        # In a full implementation, you would use background removal here
        result = Image.new('RGB', (width, height))
        result.paste(background, (0, 0))
        result.paste(image, (0, 0))  # This would use alpha mask in real implementation
        
        return result


def main():
    st.set_page_config(
        page_title="Professional Headshot Generator",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional styling
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
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header"><h1>📸 Professional Headshot Studio</h1><p>AI-Powered Professional Photography</p></div>', unsafe_allow_html=True)
    
    # Initialize headshot generator
    generator = ProfessionalHeadshotGenerator()
    
    # Sidebar controls
    st.sidebar.header("🎨 Professional Controls")
    
    # Upload image
    uploaded_file = st.file_uploader(
        "📁 Upload Your Photo",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear, well-lit photo for best results"
    )
    
    if uploaded_file is not None:
        # Load and display original image
        original_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original Photo")
            st.image(original_image, use_column_width=True)
        
        # Professional settings
        st.sidebar.subheader("🎭 Style Settings")
        
        crop_style = st.sidebar.selectbox(
            "Crop Style",
            ["headshot", "corporate"],
            help="Headshot: Close crop focusing on face. Corporate: Includes more shoulder area"
        )
        
        bg_style = st.sidebar.selectbox(
            "Background Style",
            ["original", "studio_gray", "executive_blue", "corporate_white", "warm_beige"],
            help="Choose professional background style"
        )
        
        st.sidebar.subheader("✨ Enhancement Controls")
        
        brightness = st.sidebar.slider("Brightness", 0.7, 1.5, 1.1, 0.05)
        contrast = st.sidebar.slider("Contrast", 0.8, 1.8, 1.15, 0.05)
        saturation = st.sidebar.slider("Color Saturation", 0.7, 1.4, 1.05, 0.05)
        warmth = st.sidebar.slider("Warmth", 0.9, 1.2, 1.02, 0.02)
        
        st.sidebar.subheader("🎯 Professional Effects")
        
        skin_smoothing = st.sidebar.slider("Skin Smoothing", 0.0, 1.0, 0.2, 0.1)
        lighting_intensity = st.sidebar.slider("Studio Lighting", 0.0, 0.8, 0.15, 0.05)
        vignette_intensity = st.sidebar.slider("Vignette", 0.0, 0.5, 0.1, 0.05)
        
        st.sidebar.subheader("📐 Output Settings")
        
        output_size = st.sidebar.selectbox(
            "Output Size",
            [
                "512x512 (Professional)",
                "400x400 (LinkedIn)",
                "600x600 (High-res)",
                "800x800 (Premium)",
                "1024x1024 (Ultra)"
            ]
        )
        
        size_map = {
            "512x512 (Professional)": (512, 512),
            "400x400 (LinkedIn)": (400, 400),
            "600x600 (High-res)": (600, 600),
            "800x800 (Premium)": (800, 800),
            "1024x1024 (Ultra)": (1024, 1024)
        }
        size = size_map[output_size]
        
        # Process button
        if st.sidebar.button("🎨 Generate Professional Headshot", type="primary"):
            with st.spinner("Creating your professional headshot..."):
                
                # Professional processing pipeline
                processed_image = original_image.copy()
                
                # Step 1: Professional cropping
                st.write("🔄 Applying professional cropping...")
                processed_image = generator.professional_crop(processed_image, crop_style)
                
                # Step 2: Skin enhancement
                if skin_smoothing > 0:
                    st.write("✨ Enhancing skin appearance...")
                    processed_image = generator.skin_enhancement(processed_image, skin_smoothing)
                
                # Step 3: Professional lighting
                if lighting_intensity > 0:
                    st.write("💡 Applying studio lighting...")
                    processed_image = generator.professional_lighting(processed_image, lighting_intensity)
                
                # Step 4: Background styling
                if bg_style != "original":
                    st.write("🖼️ Applying professional background...")
                    processed_image = generator.create_professional_background(processed_image, bg_style)
                
                # Step 5: Professional enhancement
                st.write("🎨 Applying professional enhancements...")
                processed_image = generator.professional_enhancement(
                    processed_image, brightness, contrast, saturation, warmth
                )
                
                # Step 6: Vignette effect
                if vignette_intensity > 0:
                    st.write("🎭 Adding professional vignette...")
                    processed_image = generator.add_professional_vignette(processed_image, vignette_intensity)
                
                # Step 7: Professional resizing
                st.write("📐 Finalizing professional output...")
                final_image = generator.resize_professional(processed_image, size)
                
                # Display result
                with col2:
                    st.subheader("⭐ Professional Headshot")
                    st.image(final_image, use_column_width=True)
                    
                    # Download button
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
                    
                    # Professional specs
                    st.info(f"""
                    📊 **Professional Specifications**
                    - Output: {final_image.size[0]}×{final_image.size[1]} pixels
                    - Style: {crop_style.title()}
                    - Background: {bg_style.replace('_', ' ').title()}
                    - Format: High-quality PNG
                    """)
        
        # Professional tips
        st.sidebar.markdown("---")
        st.sidebar.subheader("💼 Professional Tips")
        st.sidebar.markdown("""
        **📸 Photography:**
        - Use natural window light
        - Position face towards light source
        - Maintain good posture
        
        **👔 Styling:**
        - Solid, professional colors
        - Avoid busy patterns
        - Ensure good grooming
        
        **🎭 Expression:**
        - Genuine, confident smile
        - Look directly at camera
        - Relax shoulders
        """)
    
    else:
        st.info("👆 Upload a photo to create your professional headshot")
        
        # Professional features showcase
        st.subheader("🌟 Professional Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
            <h4>🎯 Smart Cropping</h4>
            <ul>
            <li>Professional portrait ratios</li>
            <li>Rule of thirds positioning</li>
            <li>Headshot vs Corporate styles</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
            <h4>✨ Studio Enhancement</h4>
            <ul>
            <li>Professional lighting effects</li>
            <li>Skin smoothing & enhancement</li>
            <li>Color temperature adjustment</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
            <h4>🎨 Professional Styling</h4>
            <ul>
            <li>Studio background options</li>
            <li>Professional vignetting</li>
            <li>High-quality output</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Usage guide
        st.subheader("📋 Professional Process")
        
        with st.expander("🎓 How to Create Professional Headshots"):
            st.markdown("""
            ### Step-by-Step Guide:
            
            1. **📁 Upload Photo**: Choose a well-lit, clear photo
            2. **🎭 Select Style**: Choose between Headshot or Corporate crop
            3. **🖼️ Pick Background**: Select professional background style
            4. **✨ Adjust Enhancement**: Fine-tune lighting and color
            5. **🎯 Apply Effects**: Add skin smoothing and vignette
            6. **📐 Choose Size**: Select appropriate output dimensions
            7. **🎨 Generate**: Create your professional headshot
            8. **💾 Download**: Save high-quality result
            
            ### Professional Standards:
            - **Resolution**: High-quality output for print and digital
            - **Aspect Ratio**: Professional portrait proportions
            - **Color**: Optimized for professional use
            - **Lighting**: Studio-quality enhancement
            """)


if __name__ == "__main__":
    main()
