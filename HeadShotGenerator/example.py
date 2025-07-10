#!/usr/bin/env python3
"""
Simple usage example for the Professional Headshot Generator
"""

from PIL import Image
import numpy as np
from app import HeadshotGenerator


def example_usage():
    """Example of how to use the HeadshotGenerator"""
    
    # Initialize the generator
    generator = HeadshotGenerator()
    
    # Load your image (replace with your image path)
    # image = Image.open("your_photo.jpg")
    
    # Example processing steps:
    # 1. Convert to numpy array for face detection
    # img_array = np.array(image)
    
    # 2. Crop to headshot
    # cropped = generator.crop_to_headshot(img_array)
    # processed_image = Image.fromarray(cropped)
    
    # 3. Apply enhancements
    # enhanced = generator.enhance_image(processed_image)
    
    # 4. Apply professional background
    # final = generator.apply_professional_background(enhanced, "white")
    
    # 5. Resize to standard dimensions
    # result = generator.resize_for_profile(final, (400, 400))
    
    # 6. Save the result
    # result.save("professional_headshot.png")
    
    print("To run the full application, use: streamlit run app.py")
    print("Or run the demo script: python demo.py")


if __name__ == "__main__":
    example_usage()
