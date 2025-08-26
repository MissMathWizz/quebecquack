#!/usr/bin/env python3
"""
Friend Photo Processing and Face Extraction System
Advanced image processing for extracting friends from photos for integration.
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import json
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import requests
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Results from friend extraction process"""
    success: bool
    extracted_image: Optional[np.ndarray] = None
    mask: Optional[np.ndarray] = None
    bounding_box: Optional[Tuple[int, int, int, int]] = None
    confidence: float = 0.0
    lighting_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class FriendExtractionProcessor:
    def __init__(self):
        self.face_cascade = None
        self.body_cascade = None
        self.setup_opencv_cascades()
        
    def setup_opencv_cascades(self):
        """Initialize OpenCV cascade classifiers"""
        try:
            # Load pre-trained cascades
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
            print("✅ OpenCV cascades loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not load OpenCV cascades: {e}")
    
    def extract_friend_from_photo(
        self, 
        image_path: str, 
        description: str = "",
        extraction_method: str = "advanced"
    ) -> ExtractionResult:
        """
        Extract a person from a photo using various methods
        
        Args:
            image_path: Path to the friend's photo
            description: Text description of the friend
            extraction_method: 'basic', 'advanced', or 'ai_segmentation'
        """
        try:
            print(f"🔍 Extracting friend from: {image_path}")
            
            # Load image
            if image_path.startswith('http'):
                # Download image if URL
                response = requests.get(image_path)
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            else:
                image = cv2.imread(image_path)
            
            if image is None:
                return ExtractionResult(
                    success=False,
                    error_message="Could not load image"
                )
            
            # Choose extraction method
            if extraction_method == "basic":
                return self._extract_basic_background_removal(image)
            elif extraction_method == "advanced":
                return self._extract_advanced_segmentation(image, description)
            elif extraction_method == "ai_segmentation":
                return self._extract_ai_segmentation(image, description)
            else:
                return ExtractionResult(
                    success=False,
                    error_message=f"Unknown extraction method: {extraction_method}"
                )
                
        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=f"Extraction failed: {str(e)}"
            )
    
    def _extract_basic_background_removal(self, image: np.ndarray) -> ExtractionResult:
        """Basic background removal using color-based segmentation"""
        try:
            print("🎯 Using basic background removal...")
            
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Detect faces to focus the extraction
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4) if self.face_cascade else []
            
            if len(faces) == 0:
                # No face detected, use center-based extraction
                height, width = image.shape[:2]
                center_region = (width//4, height//4, width//2, height//2)
                bounding_box = center_region
            else:
                # Use the largest face as reference
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Expand bounding box to include body
                expansion_factor = 2.5
                new_w = int(w * expansion_factor)
                new_h = int(h * expansion_factor * 1.5)  # Body is taller
                new_x = max(0, x - (new_w - w) // 2)
                new_y = max(0, y - (new_h - h) // 4)  # More space below face
                
                # Clamp to image bounds
                new_x = max(0, min(new_x, image.shape[1] - new_w))
                new_y = max(0, min(new_y, image.shape[0] - new_h))
                new_w = min(new_w, image.shape[1] - new_x)
                new_h = min(new_h, image.shape[0] - new_y)
                
                bounding_box = (new_x, new_y, new_w, new_h)
            
            # Extract region
            x, y, w, h = bounding_box
            extracted_region = image[y:y+h, x:x+w]
            
            # Create a basic mask (for now, just a filled rectangle)
            mask = np.zeros((h, w), dtype=np.uint8)
            
            # Create elliptical mask for more natural person shape
            center = (w//2, h//2)
            axes = (w//3, h//2)
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
            
            # Apply Gaussian blur to soften edges
            mask = cv2.GaussianBlur(mask, (21, 21), 0)
            
            # Analyze lighting
            lighting_analysis = self._analyze_lighting(extracted_region)
            
            return ExtractionResult(
                success=True,
                extracted_image=extracted_region,
                mask=mask,
                bounding_box=bounding_box,
                confidence=0.7 if len(faces) > 0 else 0.4,
                lighting_analysis=lighting_analysis
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=f"Basic extraction failed: {str(e)}"
            )
    
    def _extract_advanced_segmentation(self, image: np.ndarray, description: str) -> ExtractionResult:
        """Advanced segmentation using multiple techniques"""
        try:
            print("🚀 Using advanced segmentation...")
            
            # Start with basic extraction
            basic_result = self._extract_basic_background_removal(image)
            if not basic_result.success:
                return basic_result
            
            # Enhance the mask using edge detection and morphological operations
            x, y, w, h = basic_result.bounding_box
            extracted_region = basic_result.extracted_image
            
            # Convert to grayscale for edge detection
            gray_region = cv2.cvtColor(extracted_region, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray_region, 50, 150)
            
            # Morphological operations to close gaps
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Use the largest contour as the person outline
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Create refined mask from contour
                refined_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.fillPoly(refined_mask, [largest_contour], 255)
                
                # Apply Gaussian blur for smooth edges
                refined_mask = cv2.GaussianBlur(refined_mask, (15, 15), 0)
                
                # Combine with original mask
                combined_mask = cv2.addWeighted(basic_result.mask, 0.4, refined_mask, 0.6, 0)
            else:
                combined_mask = basic_result.mask
            
            # Additional processing based on description
            if description:
                combined_mask = self._refine_mask_with_description(
                    extracted_region, combined_mask, description
                )
            
            return ExtractionResult(
                success=True,
                extracted_image=extracted_region,
                mask=combined_mask,
                bounding_box=basic_result.bounding_box,
                confidence=min(basic_result.confidence + 0.2, 0.95),
                lighting_analysis=basic_result.lighting_analysis
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=f"Advanced extraction failed: {str(e)}"
            )
    
    def _extract_ai_segmentation(self, image: np.ndarray, description: str) -> ExtractionResult:
        """AI-powered segmentation (placeholder for future implementation)"""
        print("🤖 AI segmentation not yet implemented, falling back to advanced...")
        return self._extract_advanced_segmentation(image, description)
    
    def _refine_mask_with_description(
        self, 
        image: np.ndarray, 
        mask: np.ndarray, 
        description: str
    ) -> np.ndarray:
        """Refine extraction mask based on text description"""
        try:
            # Parse description for clues
            description_lower = description.lower()
            
            # Color-based refinements
            if 'blue' in description_lower or 'dress' in description_lower:
                # Enhance blue regions
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
                mask = cv2.addWeighted(mask, 0.8, blue_mask, 0.2, 0)
            
            if 'red' in description_lower:
                # Enhance red regions
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                red_mask1 = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
                red_mask2 = cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
                red_mask = cv2.add(red_mask1, red_mask2)
                mask = cv2.addWeighted(mask, 0.8, red_mask, 0.2, 0)
            
            # Hair-based refinements
            if 'curly' in description_lower or 'long hair' in description_lower:
                # Expand mask in upper regions for hair
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
                expanded_mask = cv2.dilate(mask, kernel, iterations=1)
                # Only keep the upper expansion
                h, w = mask.shape
                hair_region = np.zeros_like(mask)
                hair_region[:h//3, :] = 255  # Top third for hair
                expanded_hair = cv2.bitwise_and(expanded_mask, hair_region)
                mask = cv2.add(mask, expanded_hair)
            
            return mask
            
        except Exception as e:
            print(f"⚠️  Description refinement failed: {e}")
            return mask
    
    def _analyze_lighting(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze lighting conditions in the extracted image"""
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Basic statistics
            mean_brightness = np.mean(gray)
            brightness_std = np.std(gray)
            
            # Color temperature analysis
            b, g, r = cv2.split(image)
            color_temp_ratio = np.mean(b) / max(np.mean(r), 1)  # Blue/Red ratio
            
            # Contrast analysis
            contrast = brightness_std / max(mean_brightness, 1)
            
            # Shadow detection (simplified)
            shadow_threshold = mean_brightness * 0.3
            shadow_percentage = np.sum(gray < shadow_threshold) / gray.size
            
            # Determine dominant lighting
            if color_temp_ratio > 1.1:
                lighting_type = "cool"  # Bluish, overcast/indoor
            elif color_temp_ratio < 0.9:
                lighting_type = "warm"  # Reddish, sunset/incandescent
            else:
                lighting_type = "neutral"  # Balanced, daylight
            
            return {
                "brightness": float(mean_brightness),
                "contrast": float(contrast),
                "color_temperature": float(color_temp_ratio),
                "lighting_type": lighting_type,
                "shadow_percentage": float(shadow_percentage),
                "quality_score": min(1.0, (mean_brightness / 128) * (1 - shadow_percentage))
            }
            
        except Exception as e:
            print(f"⚠️  Lighting analysis failed: {e}")
            return {
                "brightness": 128.0,
                "contrast": 0.5,
                "color_temperature": 1.0,
                "lighting_type": "neutral",
                "shadow_percentage": 0.2,
                "quality_score": 0.7
            }
    
    def process_for_integration(
        self, 
        extraction_result: ExtractionResult,
        target_lighting: Dict[str, Any],
        integration_style: str = "polaroid"
    ) -> ExtractionResult:
        """Process extracted friend for integration with target photo"""
        if not extraction_result.success:
            return extraction_result
        
        try:
            print("⚙️  Processing friend for integration...")
            
            processed_image = extraction_result.extracted_image.copy()
            
            # Lighting adjustment
            processed_image = self._adjust_lighting_match(
                processed_image, 
                extraction_result.lighting_analysis,
                target_lighting
            )
            
            # Style adjustment
            if integration_style == "polaroid":
                processed_image = self._apply_polaroid_style(processed_image)
            elif integration_style == "vintage":
                processed_image = self._apply_vintage_style(processed_image)
            
            # Edge softening for better integration
            processed_mask = self._soften_mask_edges(extraction_result.mask)
            
            return ExtractionResult(
                success=True,
                extracted_image=processed_image,
                mask=processed_mask,
                bounding_box=extraction_result.bounding_box,
                confidence=extraction_result.confidence,
                lighting_analysis=self._analyze_lighting(processed_image)
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=f"Integration processing failed: {str(e)}"
            )
    
    def _adjust_lighting_match(
        self, 
        image: np.ndarray, 
        source_lighting: Dict[str, Any],
        target_lighting: Dict[str, Any]
    ) -> np.ndarray:
        """Adjust image lighting to match target conditions"""
        try:
            adjusted = image.copy()
            
            # Brightness adjustment
            brightness_diff = target_lighting.get("brightness", 128) - source_lighting.get("brightness", 128)
            if abs(brightness_diff) > 10:
                adjusted = cv2.convertScaleAbs(adjusted, alpha=1.0, beta=brightness_diff * 0.3)
            
            # Color temperature adjustment
            source_temp = source_lighting.get("color_temperature", 1.0)
            target_temp = target_lighting.get("color_temperature", 1.0)
            temp_diff = target_temp - source_temp
            
            if abs(temp_diff) > 0.1:
                # Apply color correction
                if temp_diff > 0:  # Need more blue (cooler)
                    adjusted[:, :, 0] = np.clip(adjusted[:, :, 0] * (1 + temp_diff * 0.2), 0, 255)
                else:  # Need more red (warmer)
                    adjusted[:, :, 2] = np.clip(adjusted[:, :, 2] * (1 - temp_diff * 0.2), 0, 255)
            
            return adjusted.astype(np.uint8)
            
        except Exception as e:
            print(f"⚠️  Lighting adjustment failed: {e}")
            return image
    
    def _apply_polaroid_style(self, image: np.ndarray) -> np.ndarray:
        """Apply Polaroid aesthetic to the extracted friend"""
        try:
            # Convert to PIL for easier processing
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Slightly reduce saturation
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(0.85)
            
            # Slight warmth boost
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(1.05)
            
            # Add slight blur for vintage softness
            pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Convert back to OpenCV format
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            print(f"⚠️  Polaroid style application failed: {e}")
            return image
    
    def _apply_vintage_style(self, image: np.ndarray) -> np.ndarray:
        """Apply vintage film aesthetic"""
        try:
            # Convert to PIL
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Reduce contrast slightly
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(0.9)
            
            # Add warmth
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(1.1)
            
            # Convert back
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            print(f"⚠️  Vintage style application failed: {e}")
            return image
    
    def _soften_mask_edges(self, mask: np.ndarray) -> np.ndarray:
        """Soften mask edges for seamless integration"""
        try:
            # Apply Gaussian blur
            soft_mask = cv2.GaussianBlur(mask, (21, 21), 0)
            
            # Apply feathering effect
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            eroded = cv2.erode(soft_mask, kernel, iterations=1)
            feathered = cv2.GaussianBlur(eroded, (31, 31), 0)
            
            return feathered
            
        except Exception as e:
            print(f"⚠️  Mask softening failed: {e}")
            return mask
    
    def save_extraction_result(self, result: ExtractionResult, output_dir: str, filename_prefix: str):
        """Save extraction results to disk"""
        if not result.success:
            print(f"❌ Cannot save failed extraction: {result.error_message}")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save extracted image
        if result.extracted_image is not None:
            image_path = output_path / f"{filename_prefix}_extracted_{timestamp}.png"
            cv2.imwrite(str(image_path), result.extracted_image)
            print(f"💾 Saved extracted image: {image_path}")
        
        # Save mask
        if result.mask is not None:
            mask_path = output_path / f"{filename_prefix}_mask_{timestamp}.png"
            cv2.imwrite(str(mask_path), result.mask)
            print(f"💾 Saved mask: {mask_path}")
        
        # Save metadata
        metadata = {
            "success": result.success,
            "confidence": result.confidence,
            "bounding_box": result.bounding_box,
            "lighting_analysis": result.lighting_analysis,
            "timestamp": timestamp
        }
        
        metadata_path = output_path / f"{filename_prefix}_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"💾 Saved metadata: {metadata_path}")


def main():
    """Demo the friend extraction system"""
    processor = FriendExtractionProcessor()
    
    print("🚀 Friend Extraction Processor Demo")
    print("="*50)
    
    # This would be used with actual image files
    print("📋 Usage:")
    print("  processor = FriendExtractionProcessor()")
    print("  result = processor.extract_friend_from_photo('friend.jpg', 'woman in blue dress')")
    print("  if result.success:")
    print("    processor.save_extraction_result(result, 'output/', 'friend')")
    
    print("\n✅ Friend extraction processor initialized and ready!")
    print("   Use with actual image files for real extraction results.")


if __name__ == "__main__":
    main()