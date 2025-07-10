import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Tuple


class BasicHeadshotGenerator:
    """Basic headshot generator using only PIL for image processing"""
    
    def enhance_image(self, image: Image.Image, brightness: float = 1.1, 
                     contrast: float = 1.1, saturation: float = 1.05) -> Image.Image:
        """Apply professional enhancements to the image"""
        # Brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
        
        # Contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # Saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)
        
        # Slight sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=3))
        
        return image
    
    def crop_to_center(self, image: Image.Image, crop_ratio: float = 0.8) -> Image.Image:
        """Crop image to center area for headshot effect"""
        width, height = image.size
        
        # Calculate crop dimensions
        crop_width = int(width * crop_ratio)
        crop_height = int(height * crop_ratio)
        
        # Calculate crop coordinates
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        
        return image.crop((left, top, right, bottom))
    
    def resize_for_profile(self, image: Image.Image, size: Tuple[int, int] = (400, 400)) -> Image.Image:
        """Resize image to standard profile dimensions"""
        # Calculate aspect ratio
        aspect_ratio = image.width / image.height
        
        if aspect_ratio > 1:  # Wider than tall
            new_width = size[0]
            new_height = int(size[0] / aspect_ratio)
        else:  # Taller than wide
            new_height = size[1]
            new_width = int(size[1] * aspect_ratio)
        
        # Resize maintaining aspect ratio
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create final image with padding if needed
        final_image = Image.new("RGB", size, (255, 255, 255))
        paste_x = (size[0] - new_width) // 2
        paste_y = (size[1] - new_height) // 2
        final_image.paste(image, (paste_x, paste_y))
        
        return final_image


def main():
    st.set_page_config(
        page_title="Professional Headshot Generator",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("📸 Professional Headshot Generator")
    st.markdown("Transform your photos into professional headshots with enhanced image processing")
    
    # Initialize headshot generator
    generator = BasicHeadshotGenerator()
    
    # Sidebar controls
    st.sidebar.header("Settings")
    
    # Upload image
    uploaded_file = st.file_uploader(
        "Upload your photo",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear photo of yourself for best results"
    )
    
    if uploaded_file is not None:
        # Load and display original image
        original_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(original_image, use_column_width=True)
        
        # Sidebar options
        st.sidebar.subheader("Enhancement Options")
        
        brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.1, 0.1)
        contrast = st.sidebar.slider("Contrast", 0.5, 2.0, 1.1, 0.1)
        saturation = st.sidebar.slider("Saturation", 0.5, 2.0, 1.05, 0.05)
        
        st.sidebar.subheader("Cropping Options")
        crop_ratio = st.sidebar.slider("Crop Focus", 0.5, 1.0, 0.8, 0.05)
        
        st.sidebar.subheader("Output Options")
        output_size = st.sidebar.selectbox(
            "Output Size",
            ["400x400 (LinkedIn)", "500x500 (Standard)", "600x600 (High-res)", "800x800 (Large)"]
        )
        
        size_map = {
            "400x400 (LinkedIn)": (400, 400),
            "500x500 (Standard)": (500, 500),
            "600x600 (High-res)": (600, 600),
            "800x800 (Large)": (800, 800)
        }
        size = size_map[output_size]
        
        # Process button
        if st.sidebar.button("Generate Headshot", type="primary"):
            with st.spinner("Processing your headshot..."):
                # Start with original image
                processed_image = original_image.copy()
                
                # Crop to focus area
                processed_image = generator.crop_to_center(processed_image, crop_ratio)
                
                # Apply enhancements
                processed_image = generator.enhance_image(
                    processed_image, brightness, contrast, saturation
                )
                
                # Resize to final dimensions
                final_image = generator.resize_for_profile(processed_image, size)
                
                # Display result
                with col2:
                    st.subheader("Professional Headshot")
                    st.image(final_image, use_column_width=True)
                    
                    # Download button
                    buf = io.BytesIO()
                    final_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="Download Headshot",
                        data=byte_im,
                        file_name="professional_headshot.png",
                        mime="image/png",
                        type="primary"
                    )
                    
                    # Show image info
                    st.info(f"Output size: {final_image.size[0]}x{final_image.size[1]} pixels")
        
        # Tips section
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 Tips for Best Results")
        st.sidebar.markdown("""
        - Use well-lit photos
        - Face should be centered in image
        - Avoid busy backgrounds
        - Look directly at camera
        - Professional attire recommended
        """)
    
    else:
        st.info("👆 Please upload a photo to get started")
        
        # Example section
        st.subheader("🌟 Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 Smart Cropping**
            - Center-focused cropping
            - Adjustable crop ratio
            - Multiple output sizes
            """)
        
        with col2:
            st.markdown("""
            **🎨 Professional Enhancement**
            - Brightness & contrast adjustment
            - Color saturation optimization
            - Image sharpening
            """)
        
        with col3:
            st.markdown("""
            **📱 Easy to Use**
            - Drag & drop photo upload
            - Real-time preview
            - Instant download
            """)
        
        # Instructions
        st.subheader("📋 How to Use")
        st.markdown("""
        1. **Upload** your photo using the file uploader
        2. **Adjust** the enhancement settings in the sidebar
        3. **Generate** your professional headshot
        4. **Download** the result in your preferred size
        """)


if __name__ == "__main__":
    main()
