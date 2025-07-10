#!/usr/bin/env python3
"""
Demo script for the Professional Headshot Generator

This script demonstrates the core functionality of the headshot generator.
Run this script to test the main features without the Streamlit interface.
"""

import cv2
import numpy as np
from PIL import Image
import os
import sys
from app import HeadshotGenerator

def main():
    """Main demo function"""
    print("🎯 Professional Headshot Generator Demo")
    print("=" * 50)
    
    # Initialize the generator
    generator = HeadshotGenerator()
    
    # Check if demo image exists, if not, create instructions
    demo_image_path = "demo_photo.jpg"
    
    if not os.path.exists(demo_image_path):
        print("📸 Demo Image Required")
        print(f"Please place a photo named '{demo_image_path}' in the project directory.")
        print("The photo should contain a clear face for best results.")
        print("\nTips for best results:")
        print("- Use well-lit photos")
        print("- Ensure face is clearly visible")
        print("- Avoid busy backgrounds")
        print("- Look directly at camera")
        return
    
    try:
        # Load and process the demo image
        print(f"📷 Loading demo image: {demo_image_path}")
        original_image = Image.open(demo_image_path)
        print(f"✅ Image loaded successfully: {original_image.size}")
        
        # Convert to numpy for face detection
        img_array = np.array(original_image)
        
        # Detect face
        print("🔍 Detecting face...")
        face_bbox = generator.detect_face(img_array)
        
        if face_bbox:
            print(f"✅ Face detected at: {face_bbox}")
            
            # Crop to headshot
            print("✂️ Cropping to headshot...")
            cropped = generator.crop_to_headshot(img_array)
            processed_image = Image.fromarray(cropped)
            
            # Apply enhancements
            print("✨ Applying professional enhancements...")
            enhanced_image = generator.enhance_image(
                processed_image, 
                brightness=1.1, 
                contrast=1.1, 
                saturation=1.05
            )
            
            # Apply background (optional - might take time to download models)
            print("🖼️ Processing background...")
            try:
                final_image = generator.apply_professional_background(
                    enhanced_image, "light_gray"
                )
                print("✅ Background processing complete")
            except Exception as e:
                print(f"⚠️ Background processing skipped: {e}")
                final_image = enhanced_image
            
            # Resize to standard profile size
            print("📏 Resizing to standard profile dimensions...")
            final_image = generator.resize_for_profile(final_image, (400, 400))
            
            # Save the result
            output_path = "demo_headshot_output.png"
            final_image.save(output_path)
            print(f"💾 Professional headshot saved as: {output_path}")
            
            # Show comparison
            print("\n📊 Processing Summary:")
            print(f"Original size: {original_image.size}")
            print(f"Final size: {final_image.size}")
            print(f"Face detected: Yes")
            print(f"Output file: {output_path}")
            
        else:
            print("❌ No face detected in the image.")
            print("Please try with a different image where the face is more clearly visible.")
            
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        print("Please check that the image file is valid and not corrupted.")

if __name__ == "__main__":
    main()
