import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import mediapipe as mp


class AdvancedHeadshotProcessor:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.7
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7
        )
    
    def skin_smoothing(self, image: np.ndarray, 
                      intensity: float = 0.7) -> np.ndarray:
        """Apply skin smoothing using bilateral filter"""
        # Convert to float for processing
        img_float = image.astype(np.float32) / 255.0
        
        # Apply bilateral filter for skin smoothing
        smoothed = cv2.bilateralFilter(img_float, 15, 80, 80)
        
        # Blend with original
        result = cv2.addWeighted(img_float, 1 - intensity, smoothed, intensity, 0)
        
        # Convert back to uint8
        return (result * 255).astype(np.uint8)
    
    def enhance_eyes(self, image: np.ndarray) -> np.ndarray:
        """Enhance eyes by increasing local contrast"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        enhanced = cv2.merge([l, a, b])
        
        # Convert back to BGR
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    def add_subtle_vignette(self, image: Image.Image, intensity: float = 0.3) -> Image.Image:
        """Add subtle vignette effect"""
        width, height = image.size
        
        # Create vignette mask
        vignette = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(vignette)
        
        # Create radial gradient
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2
        
        for radius in range(max_radius, 0, -1):
            alpha = int(255 * (1 - intensity * (max_radius - radius) / max_radius))
            draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], fill=alpha)
        
        # Apply vignette
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=max_radius // 4))
        
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create dark overlay
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Apply vignette mask
        result = Image.composite(image, overlay, vignette)
        
        return result.convert('RGB')
    
    def professional_lighting(self, image: np.ndarray) -> np.ndarray:
        """Simulate professional lighting"""
        # Convert to float
        img_float = image.astype(np.float32) / 255.0
        
        # Create a soft light effect
        height, width = img_float.shape[:2]
        
        # Create light source (top-left bias)
        y, x = np.ogrid[:height, :width]
        light_x, light_y = width * 0.3, height * 0.2
        
        # Calculate distance from light source
        distance = np.sqrt((x - light_x)**2 + (y - light_y)**2)
        max_distance = np.sqrt(width**2 + height**2)
        
        # Normalize and invert
        light_map = 1 - (distance / max_distance)
        light_map = np.power(light_map, 0.5)  # Adjust falloff
        
        # Apply light map
        for i in range(3):  # RGB channels
            img_float[:, :, i] = img_float[:, :, i] * (0.7 + 0.3 * light_map)
        
        # Clamp values
        img_float = np.clip(img_float, 0, 1)
        
        return (img_float * 255).astype(np.uint8)
    
    def process_professional_headshot(self, image: Image.Image, 
                                    skin_smooth: bool = True,
                                    enhance_eyes: bool = True,
                                    add_vignette: bool = True,
                                    professional_light: bool = True) -> Image.Image:
        """Apply all professional enhancements"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply skin smoothing
        if skin_smooth:
            img_array = self.skin_smoothing(img_array)
        
        # Enhance eyes
        if enhance_eyes:
            img_array = self.enhance_eyes(img_array)
        
        # Apply professional lighting
        if professional_light:
            img_array = self.professional_lighting(img_array)
        
        # Convert back to PIL
        processed_image = Image.fromarray(img_array)
        
        # Add vignette
        if add_vignette:
            processed_image = self.add_subtle_vignette(processed_image)
        
        return processed_image
