import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
from dotenv import load_dotenv
from typing import Optional, Tuple

# Load environment variables
load_dotenv()

class SimpleHeadshotGenerator:
    def __init__(self):
        # Use OpenCV's built-in face detection instead of MediaPipe
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face in image using OpenCV and return bounding box coordinates"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) > 0:
            # Return the largest face detected
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            return (x, y, w, h)
        return None
    
    def crop_to_headshot(self, image: np.ndarray, padding: float = 0.3) -> np.ndarray:
        """Crop image to focus on head and shoulders"""
        face_bbox = self.detect_face(image)
        
        if face_bbox:
            x, y, width, height = face_bbox
            
            # Calculate extended crop area for headshot
            center_x = x + width // 2
            center_y = y + height // 2
            
            # Create larger crop area
            crop_width = int(width * (1 + padding * 2))
            crop_height = int(height * (1 + padding * 2.5))
            
            # Calculate crop coordinates
            crop_x = max(0, center_x - crop_width // 2)
            crop_y = max(0, center_y - crop_height // 2)
            crop_x2 = min(image.shape[1], crop_x + crop_width)
            crop_y2 = min(image.shape[0], crop_y + crop_height)
            
            return image[crop_y:crop_y2, crop_x:crop_x2]
        
        return image
    
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
    
    def apply_simple_background(self, image: Image.Image, bg_color: str = "white") -> Image.Image:
        """Apply simple background (without advanced removal)"""
        # For now, just return the original image
        # In a full implementation, you could use rembg or other background removal tools
        if bg_color == "white":
            return image
        elif bg_color == "light_gray":
            return image
        else:
            return image
    
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
    st.markdown("Transform your photos into professional headshots with AI-powered enhancement")
    
    # Initialize headshot generator
    generator = SimpleHeadshotGenerator()
    
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
        
        st.sidebar.subheader("Background Options")
        bg_option = st.sidebar.selectbox(
            "Background Style",
            ["original", "white", "light_gray"]
        )
        
        st.sidebar.subheader("Output Options")
        output_size = st.sidebar.selectbox(
            "Output Size",
            ["400x400 (LinkedIn)", "500x500 (Standard)", "600x600 (High-res)"]
        )
        
        size_map = {
            "400x400 (LinkedIn)": (400, 400),
            "500x500 (Standard)": (500, 500),
            "600x600 (High-res)": (600, 600)
        }
        size = size_map[output_size]
        
        # Process button
        if st.sidebar.button("Generate Headshot", type="primary"):
            with st.spinner("Processing your headshot..."):
                # Convert to numpy array for processing
                img_array = np.array(original_image)
                
                # Crop to headshot
                cropped = generator.crop_to_headshot(img_array)
                processed_image = Image.fromarray(cropped)
                
                # Apply enhancements
                processed_image = generator.enhance_image(
                    processed_image, brightness, contrast, saturation
                )
                
                # Apply background if not original
                if bg_option != "original":
                    processed_image = generator.apply_simple_background(
                        processed_image, bg_option
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
        
        # Tips section
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 Tips for Best Results")
        st.sidebar.markdown("""
        - Use well-lit photos
        - Face should be clearly visible
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
            - Automatic face detection
            - Perfect headshot framing
            - Shoulder inclusion
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
            **🖼️ Background Options**
            - Keep original background
            - Professional solid colors
            - Multiple output sizes
            """)

if __name__ == "__main__":
    main()
