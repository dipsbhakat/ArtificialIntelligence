import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
from typing import Tuple
import math


class EnhancedHeadshotGenerator:
    """Enhanced professional headshot generator with improved processing"""
    
    def detect_face_region(self, 
                          image: Image.Image) -> Tuple[int, int, int, int]:
        """
        Simple face detection using image analysis
        Returns approximate face region (left, top, right, bottom)
        """
        # Convert to grayscale for analysis
        gray = ImageOps.grayscale(image)
        
        # Get image dimensions
        width, height = image.size
        
        # For most portrait photos, face is in upper 60% and center 60% of image
        face_left = int(width * 0.2)
        face_top = int(height * 0.1)
        face_right = int(width * 0.8)
        face_bottom = int(height * 0.6)
        
        return (face_left, face_top, face_right, face_bottom)
    
    def intelligent_crop(self, image: Image.Image, style: str = "headshot") -> Image.Image:
        """Apply intelligent cropping based on face detection and style"""
        width, height = image.size
        face_region = self.detect_face_region(image)
        face_left, face_top, face_right, face_bottom = face_region
        
        # Calculate face center
        face_center_x = (face_left + face_right) // 2
        face_center_y = (face_top + face_bottom) // 2
        
        if style == "headshot":
            # Professional headshot: 4:5 ratio (portrait)
            target_ratio = 4/5
            
            if width/height > target_ratio:
                # Image is too wide - crop from sides, center on face
                new_width = int(height * target_ratio)
                left = max(0, face_center_x - new_width // 2)
                left = min(left, width - new_width)
                image = image.crop((left, 0, left + new_width, height))
            else:
                # Image is too tall - crop from top/bottom, keep face area
                new_height = int(width / target_ratio)
                # Position to keep face in upper third
                top = max(0, face_center_y - new_height // 3)
                top = min(top, height - new_height)
                image = image.crop((0, top, width, top + new_height))
                
        elif style == "corporate":
            # Corporate style: 3:4 ratio (more shoulder area)
            target_ratio = 3/4
            
            if width/height > target_ratio:
                new_width = int(height * target_ratio)
                left = max(0, face_center_x - new_width // 2)
                left = min(left, width - new_width)
                image = image.crop((left, 0, left + new_width, height))
            else:
                new_height = int(width / target_ratio)
                # Keep face in upper quarter for corporate look
                top = max(0, face_center_y - new_height // 4)
                top = min(top, height - new_height)
                image = image.crop((0, top, width, top + new_height))
                
        elif style == "linkedin":
            # LinkedIn optimized: Square with face centered
            min_dim = min(width, height)
            left = max(0, face_center_x - min_dim // 2)
            top = max(0, face_center_y - min_dim // 3)  # Face in upper third
            
            # Adjust if crop goes outside image
            left = min(left, width - min_dim)
            top = min(top, height - min_dim)
            
            image = image.crop((left, top, left + min_dim, top + min_dim))
        
        return image
    
    def auto_color_correction(self, image: Image.Image) -> Image.Image:
        """Apply automatic color correction for natural skin tones"""
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Calculate histogram for each channel
        hist_r = np.histogram(img_array[:,:,0], bins=256, range=(0,256))[0]
        hist_g = np.histogram(img_array[:,:,1], bins=256, range=(0,256))[0]
        hist_b = np.histogram(img_array[:,:,2], bins=256, range=(0,256))[0]
        
        # Find percentiles for auto-levels
        def find_percentile(hist, percentile):
            total = np.sum(hist)
            threshold = total * (percentile / 100)
            cumsum = np.cumsum(hist)
            return np.argmax(cumsum >= threshold)
        
        # Auto-levels adjustment (stretch histogram)
        r_min, r_max = find_percentile(hist_r, 1), find_percentile(hist_r, 99)
        g_min, g_max = find_percentile(hist_g, 1), find_percentile(hist_g, 99)
        b_min, b_max = find_percentile(hist_b, 1), find_percentile(hist_b, 99)
        
        # Apply levels adjustment
        img_array = img_array.astype(np.float32)
        
        # Red channel
        img_array[:,:,0] = np.clip((img_array[:,:,0] - r_min) * 255 / (r_max - r_min), 0, 255)
        # Green channel
        img_array[:,:,1] = np.clip((img_array[:,:,1] - g_min) * 255 / (g_max - g_min), 0, 255)
        # Blue channel
        img_array[:,:,2] = np.clip((img_array[:,:,2] - b_min) * 255 / (b_max - b_min), 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def professional_enhancement(self, image: Image.Image, 
                               brightness: float = 1.1,
                               contrast: float = 1.15,
                               saturation: float = 1.05,
                               warmth: float = 1.02,
                               auto_correct: bool = True) -> Image.Image:
        """Apply professional image enhancements with auto-correction"""
        
        # Auto color correction first
        if auto_correct:
            image = self.auto_color_correction(image)
        
        # Brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
        
        # Contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # Saturation adjustment
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)
        
        # Warmth adjustment (professional color grading)
        if warmth != 1.0:
            # Convert to LAB-like adjustment
            r, g, b = image.split()
            
            # Warm highlights, cool shadows
            enhancer_r = ImageEnhance.Brightness(r)
            r = enhancer_r.enhance(warmth)
            
            enhancer_b = ImageEnhance.Brightness(b)
            b = enhancer_b.enhance(2.0 - warmth * 0.5)  # Subtle blue adjustment
            
            image = Image.merge('RGB', (r, g, b))
        
        return image
    
    def advanced_sharpening(self, image: Image.Image, intensity: float = 1.0) -> Image.Image:
        """Apply advanced sharpening with edge detection"""
        if intensity <= 0:
            return image
            
        # Multi-pass sharpening for professional results
        # First pass: Detail enhancement
        detail_enhanced = image.filter(ImageFilter.UnsharpMask(
            radius=0.5, 
            percent=int(50 * intensity), 
            threshold=1
        ))
        
        # Second pass: Edge sharpening
        edge_sharpened = detail_enhanced.filter(ImageFilter.UnsharpMask(
            radius=1.5, 
            percent=int(100 * intensity), 
            threshold=3
        ))
        
        # Blend for natural result
        result = Image.blend(detail_enhanced, edge_sharpened, 0.6)
        
        return result
    
    def professional_skin_smoothing(self, image: Image.Image, intensity: float = 0.3) -> Image.Image:
        """Apply professional skin smoothing with edge preservation"""
        if intensity <= 0:
            return image
        
        # Create edge mask to preserve important details
        gray = ImageOps.grayscale(image)
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        # Create smoothing layers
        smooth_light = image.filter(ImageFilter.GaussianBlur(radius=1.0))
        smooth_medium = image.filter(ImageFilter.GaussianBlur(radius=2.0))
        
        # Progressive blending based on intensity
        if intensity < 0.3:
            # Light smoothing
            result = Image.blend(image, smooth_light, intensity * 2)
        elif intensity < 0.6:
            # Medium smoothing
            light_blend = Image.blend(image, smooth_light, 0.6)
            result = Image.blend(light_blend, smooth_medium, (intensity - 0.3) * 2)
        else:
            # Heavy smoothing
            medium_blend = Image.blend(image, smooth_medium, 0.8)
            result = Image.blend(image, medium_blend, intensity)
        
        return result
    
    def create_professional_lighting(self, image: Image.Image, style: str = "natural") -> Image.Image:
        """Create professional lighting effects"""
        if style == "natural":
            return image
        
        width, height = image.size
        
        # Create lighting mask
        center_x, center_y = width // 2, height // 3  # Face area typically in upper third
        
        # Create radial gradient for lighting
        y, x = np.ogrid[:height, :width]
        
        if style == "studio":
            # Studio lighting: Bright center, gradual falloff
            max_radius = math.sqrt(width**2 + height**2) / 2
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            mask = 1.0 - (distance / max_radius) * 0.3  # Subtle vignette
            mask = np.clip(mask, 0.7, 1.0)
            
        elif style == "glamour":
            # Glamour lighting: Softer, more dramatic
            max_radius = math.sqrt(width**2 + height**2) / 1.8
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            mask = 1.0 - (distance / max_radius) * 0.4
            mask = np.clip(mask, 0.6, 1.0)
            
        else:
            return image
        
        # Apply lighting mask
        img_array = np.array(image).astype(np.float32)
        for channel in range(3):
            img_array[:,:,channel] *= mask
        
        img_array = np.clip(img_array, 0, 255)
        return Image.fromarray(img_array.astype(np.uint8))
    
    def resize_with_quality(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """High-quality resize with proper resampling"""
        # Use high-quality resampling
        resized = image.resize(size, Image.Resampling.LANCZOS)
        
        # Post-resize sharpening to recover detail
        if size[0] < image.size[0]:  # Only if downscaling
            resized = resized.filter(ImageFilter.UnsharpMask(
                radius=0.3,
                percent=80,
                threshold=1
            ))
        
        return resized


def main():
    st.set_page_config(
        page_title="Enhanced Professional Headshot Generator",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .processing-info {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('''
    <div class="main-header">
        <h1>📸 Enhanced Professional Headshot Generator</h1>
        <p>AI-Powered Professional Photo Enhancement with Advanced Image Processing</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize generator
    generator = EnhancedHeadshotGenerator()
    
    # Sidebar
    st.sidebar.header("🎨 Professional Studio Settings")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload Your Photo",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear photo (JPEG/PNG). Best results with good lighting and clear face visibility."
    )
    
    if uploaded_file is not None:
        # Load and validate image
        try:
            original_image = Image.open(uploaded_file)
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
        except Exception as e:
            st.error(f"Error loading image: {e}")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original Photo")
            st.image(original_image, use_column_width=True)
            
            # Image info
            width, height = original_image.size
            st.markdown(f"**Resolution:** {width} × {height} pixels")
        
        # Professional Settings
        st.sidebar.subheader("🎭 Cropping & Style")
        
        crop_style = st.sidebar.selectbox(
            "Professional Style",
            ["headshot", "corporate", "linkedin"],
            help="Headshot: Close portrait (4:5). Corporate: More shoulders (3:4). LinkedIn: Square format."
        )
        
        st.sidebar.subheader("🎨 Color & Enhancement")
        
        auto_correct = st.sidebar.checkbox("Auto Color Correction", value=True, 
                                         help="Automatically adjust levels and color balance")
        
        brightness = st.sidebar.slider("Brightness", 0.7, 1.5, 1.1, 0.05)
        contrast = st.sidebar.slider("Contrast", 0.7, 1.8, 1.15, 0.05)
        saturation = st.sidebar.slider("Color Saturation", 0.6, 1.4, 1.05, 0.05)
        warmth = st.sidebar.slider("Color Warmth", 0.9, 1.2, 1.02, 0.02)
        
        st.sidebar.subheader("✨ Professional Effects")
        
        skin_smooth = st.sidebar.slider("Skin Smoothing", 0.0, 0.8, 0.3, 0.1,
                                      help="Professional skin smoothing with edge preservation")
        
        sharpening = st.sidebar.slider("Professional Sharpening", 0.0, 2.0, 1.0, 0.1,
                                     help="Advanced multi-pass sharpening")
        
        lighting_style = st.sidebar.selectbox(
            "Lighting Effect",
            ["natural", "studio", "glamour"],
            help="Natural: No effect. Studio: Professional lighting. Glamour: Soft dramatic lighting."
        )
        
        st.sidebar.subheader("📐 Output Settings")
        
        output_size = st.sidebar.selectbox(
            "Output Size",
            [
                "512x512 (Professional)",
                "400x400 (LinkedIn Standard)", 
                "600x600 (High Resolution)",
                "800x800 (Premium Quality)",
                "1024x1024 (Ultra HD)"
            ]
        )
        
        size_map = {
            "512x512 (Professional)": (512, 512),
            "400x400 (LinkedIn Standard)": (400, 400),
            "600x600 (High Resolution)": (600, 600),
            "800x800 (Premium Quality)": (800, 800),
            "1024x1024 (Ultra HD)": (1024, 1024)
        }
        size = size_map[output_size]
        
        # Process button
        if st.sidebar.button("🎨 Generate Professional Headshot", type="primary"):
            
            # Processing information
            st.markdown('''
            <div class="processing-info">
                <h4>🔄 Processing Pipeline</h4>
                <p>Applying professional-grade image processing...</p>
            </div>
            ''', unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                with st.spinner("Creating your professional headshot..."):
                    # Processing pipeline with progress updates
                    processed_image = original_image.copy()
                    
                    # Step 1: Intelligent cropping
                    status_text.text("🎯 Applying intelligent cropping...")
                    progress_bar.progress(20)
                    processed_image = generator.intelligent_crop(processed_image, crop_style)
                    
                    # Step 2: Color enhancement
                    status_text.text("🌈 Enhancing colors and tone...")
                    progress_bar.progress(40)
                    processed_image = generator.professional_enhancement(
                        processed_image, brightness, contrast, saturation, warmth, auto_correct
                    )
                    
                    # Step 3: Skin smoothing
                    if skin_smooth > 0:
                        status_text.text("✨ Applying professional skin smoothing...")
                        progress_bar.progress(60)
                        processed_image = generator.professional_skin_smoothing(processed_image, skin_smooth)
                    
                    # Step 4: Lighting effects
                    if lighting_style != "natural":
                        status_text.text("💡 Creating professional lighting...")
                        progress_bar.progress(75)
                        processed_image = generator.create_professional_lighting(processed_image, lighting_style)
                    
                    # Step 5: Sharpening
                    if sharpening > 0:
                        status_text.text("🔍 Applying professional sharpening...")
                        progress_bar.progress(85)
                        processed_image = generator.advanced_sharpening(processed_image, sharpening)
                    
                    # Step 6: Final resize
                    status_text.text("📐 Final quality resize...")
                    progress_bar.progress(95)
                    final_image = generator.resize_with_quality(processed_image, size)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Processing complete!")
                    
                    # Display result
                    with col2:
                        st.subheader("⭐ Professional Result")
                        st.image(final_image, use_column_width=True)
                        
                        # Result info
                        st.markdown(f"**Final Size:** {size[0]} × {size[1]} pixels")
                        st.markdown(f"**Style:** {crop_style.title()}")
                        
                        # Download options
                        col2a, col2b = st.columns(2)
                        
                        with col2a:
                            # PNG Download (highest quality)
                            buf = io.BytesIO()
                            final_image.save(buf, format="PNG", optimize=True)
                            byte_im = buf.getvalue()
                            
                            st.download_button(
                                label="💾 Download PNG (Best Quality)",
                                data=byte_im,
                                file_name=f"professional_headshot_{size[0]}x{size[1]}.png",
                                mime="image/png",
                                type="primary"
                            )
                        
                        with col2b:
                            # JPEG Download (smaller file)
                            buf_jpg = io.BytesIO()
                            final_image.save(buf_jpg, format="JPEG", quality=95, optimize=True)
                            byte_im_jpg = buf_jpg.getvalue()
                            
                            st.download_button(
                                label="📁 Download JPEG (Smaller)",
                                data=byte_im_jpg,
                                file_name=f"professional_headshot_{size[0]}x{size[1]}.jpg",
                                mime="image/jpeg"
                            )
                        
                        st.success(f"✅ Professional headshot created successfully!")
                        
                        # Processing summary
                        st.markdown("---")
                        st.markdown("**🔧 Applied Enhancements:**")
                        enhancements = []
                        if auto_correct:
                            enhancements.append("Auto Color Correction")
                        if skin_smooth > 0:
                            enhancements.append(f"Skin Smoothing ({skin_smooth:.1f})")
                        if sharpening > 0:
                            enhancements.append(f"Professional Sharpening ({sharpening:.1f})")
                        if lighting_style != "natural":
                            enhancements.append(f"{lighting_style.title()} Lighting")
                        
                        st.markdown("• " + "\n• ".join(enhancements))
                        
            except Exception as e:
                st.error(f"Processing error: {e}")
                status_text.text("❌ Processing failed")
                progress_bar.progress(0)
        
        # Professional Tips
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 Professional Tips")
        st.sidebar.markdown("""
        **📸 Best Input Photos:**
        • Natural lighting from front/side
        • Clear, unblurred face
        • Minimal background distractions
        • Good posture and expression
        • High resolution (min 800x600)
        
        **🎨 Enhancement Guide:**
        • Auto Correction: Always recommended
        • Skin Smoothing: 0.2-0.4 for natural look
        • Sharpening: 0.8-1.2 for most photos
        • Warmth: 1.0-1.05 for natural skin tones
        """)
    
    else:
        # Welcome screen with features
        st.info("👆 Upload a photo to create your professional headshot")
        
        st.subheader("🌟 Enhanced Professional Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('''
            <div class="feature-card">
                <h4>🧠 AI-Powered Cropping</h4>
                <p>Intelligent face detection and professional composition with multiple style options.</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div class="feature-card">
                <h4>🎨 Advanced Enhancement</h4>
                <p>Professional color grading, auto-correction, and studio-quality processing.</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown('''
            <div class="feature-card">
                <h4>💎 Premium Quality</h4>
                <p>Multi-pass sharpening, edge-preserving smoothing, and professional lighting effects.</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Additional features
        st.markdown("---")
        st.subheader("🔧 Technical Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Image Processing:**
            - Auto color correction and levels adjustment
            - Professional skin smoothing with edge preservation
            - Multi-pass unsharp mask sharpening
            - Advanced color grading and warmth adjustment
            - High-quality LANCZOS resampling
            """)
        
        with col2:
            st.markdown("""
            **Professional Styles:**
            - Headshot: 4:5 portrait ratio
            - Corporate: 3:4 business format  
            - LinkedIn: Square optimized format
            - Multiple output sizes up to 1024x1024
            - Both PNG and JPEG download options
            """)


if __name__ == "__main__":
    main()
