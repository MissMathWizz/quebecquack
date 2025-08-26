#!/usr/bin/env python3
"""
Integration Mask Generation System
Generates precise masks for seamless friend integration into family photos.
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter
from dataclasses import dataclass
import requests


@dataclass
class MaskGenerationResult:
    """Result from mask generation process"""
    success: bool
    integration_mask: Optional[np.ndarray] = None
    placement_region: Optional[Tuple[int, int, int, int]] = None
    confidence: float = 0.0
    composition_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class IntegrationMaskGenerator:
    def __init__(self):
        self.face_cascade = None
        self.setup_detection_models()
    
    def setup_detection_models(self):
        """Initialize detection models"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("✅ Detection models initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize detection models: {e}")
    
    def generate_integration_mask(
        self,
        original_image: np.ndarray,
        friend_dimensions: Tuple[int, int],
        placement: str = "right",
        friend_description: str = "",
        preserve_subjects: bool = True
    ) -> MaskGenerationResult:
        """
        Generate integration mask for placing friend in original photo
        
        Args:
            original_image: The original family photo
            friend_dimensions: (width, height) of friend to be integrated
            placement: "left", "right", "center", "background"
            friend_description: Description of friend for context
            preserve_subjects: Whether to avoid covering existing people
        """
        try:
            print(f"🎭 Generating integration mask for {placement} placement...")
            
            # Analyze original image composition
            composition = self._analyze_composition(original_image, preserve_subjects)
            
            # Determine optimal placement region
            placement_region = self._calculate_placement_region(
                original_image, friend_dimensions, placement, composition
            )
            
            # Generate mask based on placement and composition
            mask = self._create_integration_mask(
                original_image, placement_region, friend_dimensions, composition
            )
            
            # Refine mask based on friend description
            if friend_description:
                mask = self._refine_mask_with_context(mask, friend_description, placement_region)
            
            # Calculate confidence score
            confidence = self._calculate_mask_confidence(mask, placement_region, composition)
            
            return MaskGenerationResult(
                success=True,
                integration_mask=mask,
                placement_region=placement_region,
                confidence=confidence,
                composition_analysis=composition
            )
            
        except Exception as e:
            return MaskGenerationResult(
                success=False,
                error_message=f"Mask generation failed: {str(e)}"
            )
    
    def _analyze_composition(
        self, 
        image: np.ndarray, 
        preserve_subjects: bool = True
    ) -> Dict[str, Any]:
        """Analyze image composition for optimal friend placement"""
        try:
            height, width = image.shape[:2]
            
            # Detect faces and people
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = []
            if self.face_cascade:
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Analyze lighting and color distribution
            lighting_analysis = self._analyze_scene_lighting(image)
            
            # Detect empty/background regions
            empty_regions = self._detect_empty_regions(image, faces if preserve_subjects else [])
            
            # Analyze depth and perspective cues
            depth_analysis = self._analyze_depth_cues(image)
            
            # Create occupation map (where people/objects are)
            occupation_map = self._create_occupation_map(image, faces)
            
            return {
                "image_size": (width, height),
                "detected_faces": faces.tolist() if len(faces) > 0 else [],
                "lighting_analysis": lighting_analysis,
                "empty_regions": empty_regions,
                "depth_analysis": depth_analysis,
                "occupation_map": occupation_map,
                "safe_zones": self._identify_safe_zones(occupation_map)
            }
            
        except Exception as e:
            print(f"⚠️  Composition analysis failed: {e}")
            return {
                "image_size": image.shape[:2][::-1],
                "detected_faces": [],
                "lighting_analysis": {},
                "empty_regions": [],
                "depth_analysis": {},
                "occupation_map": None,
                "safe_zones": []
            }
    
    def _analyze_scene_lighting(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze lighting conditions in the scene"""
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Divide image into regions for lighting analysis
            h, w = gray.shape
            regions = {
                "top_left": gray[:h//2, :w//2],
                "top_right": gray[:h//2, w//2:],
                "bottom_left": gray[h//2:, :w//2],
                "bottom_right": gray[h//2:, w//2:],
                "center": gray[h//4:3*h//4, w//4:3*w//4]
            }
            
            region_brightness = {}
            for name, region in regions.items():
                region_brightness[name] = {
                    "mean": float(np.mean(region)),
                    "std": float(np.std(region)),
                    "min": float(np.min(region)),
                    "max": float(np.max(region))
                }
            
            # Overall lighting characteristics
            overall_brightness = np.mean(gray)
            contrast_level = np.std(gray)
            
            # Color temperature analysis
            b, g, r = cv2.split(image)
            color_temp_ratio = np.mean(b) / max(np.mean(r), 1)
            
            return {
                "overall_brightness": float(overall_brightness),
                "contrast_level": float(contrast_level),
                "color_temperature": float(color_temp_ratio),
                "region_brightness": region_brightness,
                "lighting_direction": self._estimate_lighting_direction(region_brightness),
                "lighting_quality": "good" if contrast_level > 20 else "low"
            }
            
        except Exception as e:
            print(f"⚠️  Lighting analysis failed: {e}")
            return {}
    
    def _estimate_lighting_direction(self, region_brightness: Dict) -> str:
        """Estimate primary lighting direction from brightness analysis"""
        try:
            # Compare brightness across regions
            left_brightness = (region_brightness["top_left"]["mean"] + 
                             region_brightness["bottom_left"]["mean"]) / 2
            right_brightness = (region_brightness["top_right"]["mean"] + 
                              region_brightness["bottom_right"]["mean"]) / 2
            top_brightness = (region_brightness["top_left"]["mean"] + 
                            region_brightness["top_right"]["mean"]) / 2
            bottom_brightness = (region_brightness["bottom_left"]["mean"] + 
                               region_brightness["bottom_right"]["mean"]) / 2
            
            # Determine primary direction
            if left_brightness > right_brightness + 10:
                return "left"
            elif right_brightness > left_brightness + 10:
                return "right"
            elif top_brightness > bottom_brightness + 10:
                return "top"
            elif bottom_brightness > top_brightness + 10:
                return "bottom"
            else:
                return "center"
                
        except:
            return "center"
    
    def _detect_empty_regions(
        self, 
        image: np.ndarray, 
        faces: List[Tuple[int, int, int, int]]
    ) -> List[Dict[str, Any]]:
        """Detect regions suitable for friend placement"""
        try:
            height, width = image.shape[:2]
            
            # Create binary mask of occupied areas
            occupied_mask = np.zeros((height, width), dtype=np.uint8)
            
            # Mark face regions as occupied (with expansion)
            for (x, y, w, h) in faces:
                # Expand face region to include likely body area
                expanded_w = int(w * 2.5)
                expanded_h = int(h * 3.0)
                expanded_x = max(0, x - (expanded_w - w) // 2)
                expanded_y = max(0, y - (expanded_h - h) // 4)
                
                # Clamp to image bounds
                expanded_x = max(0, min(expanded_x, width - expanded_w))
                expanded_y = max(0, min(expanded_y, height - expanded_h))
                expanded_w = min(expanded_w, width - expanded_x)
                expanded_h = min(expanded_h, height - expanded_y)
                
                cv2.rectangle(occupied_mask, 
                            (expanded_x, expanded_y), 
                            (expanded_x + expanded_w, expanded_y + expanded_h), 
                            255, -1)
            
            # Find empty regions
            empty_mask = cv2.bitwise_not(occupied_mask)
            
            # Find contours of empty regions
            contours, _ = cv2.findContours(empty_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            empty_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 5000:  # Minimum area for friend placement
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate region properties
                    region_image = image[y:y+h, x:x+w]
                    avg_brightness = np.mean(cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY))
                    
                    empty_regions.append({
                        "bounds": (x, y, w, h),
                        "area": area,
                        "avg_brightness": float(avg_brightness),
                        "suitability": self._calculate_region_suitability(x, y, w, h, width, height)
                    })
            
            # Sort by suitability
            empty_regions.sort(key=lambda x: x["suitability"], reverse=True)
            
            return empty_regions
            
        except Exception as e:
            print(f"⚠️  Empty region detection failed: {e}")
            return []
    
    def _calculate_region_suitability(
        self, 
        x: int, y: int, w: int, h: int, 
        img_width: int, img_height: int
    ) -> float:
        """Calculate how suitable a region is for friend placement"""
        try:
            # Factors affecting suitability:
            # 1. Size (larger is better, up to a point)
            size_score = min(1.0, (w * h) / (img_width * img_height * 0.3))
            
            # 2. Aspect ratio (person-like ratios are better)
            aspect_ratio = h / max(w, 1)
            aspect_score = 1.0 - abs(aspect_ratio - 2.0) / 2.0  # Ideal ratio ~2:1
            aspect_score = max(0.0, aspect_score)
            
            # 3. Position (sides are often better than center)
            center_x = x + w // 2
            position_score = 0.8
            if center_x < img_width * 0.3 or center_x > img_width * 0.7:
                position_score = 1.0  # Prefer sides
            
            # 4. Not too close to edges
            edge_distance = min(x, y, img_width - (x + w), img_height - (y + h))
            edge_score = min(1.0, edge_distance / 20)  # Penalize if too close to edge
            
            # Combine scores
            total_score = (size_score * 0.4 + aspect_score * 0.3 + 
                          position_score * 0.2 + edge_score * 0.1)
            
            return total_score
            
        except:
            return 0.5
    
    def _analyze_depth_cues(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze depth cues for realistic friend placement"""
        try:
            # Blur analysis (out of focus areas suggest background)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Perspective analysis (simple geometric cues)
            height, width = image.shape[:2]
            
            # Analyze regions for focus/blur
            regions = {
                "foreground": gray[int(height*0.6):, :],  # Bottom part often foreground
                "background": gray[:int(height*0.4), :],  # Top part often background
                "left": gray[:, :width//3],
                "right": gray[:, 2*width//3:],
                "center": gray[:, width//3:2*width//3]
            }
            
            region_focus = {}
            for name, region in regions.items():
                if region.size > 0:
                    region_focus[name] = float(cv2.Laplacian(region, cv2.CV_64F).var())
                else:
                    region_focus[name] = 0.0
            
            return {
                "overall_focus": float(laplacian_var),
                "region_focus": region_focus,
                "depth_layers": self._estimate_depth_layers(region_focus)
            }
            
        except Exception as e:
            print(f"⚠️  Depth analysis failed: {e}")
            return {}
    
    def _estimate_depth_layers(self, region_focus: Dict[str, float]) -> List[str]:
        """Estimate depth layers from focus analysis"""
        try:
            # Sort regions by focus (higher = more in focus = closer)
            sorted_regions = sorted(region_focus.items(), key=lambda x: x[1], reverse=True)
            
            # Simple depth layering
            if len(sorted_regions) >= 2:
                foreground = sorted_regions[0][0]
                background = sorted_regions[-1][0]
                return [foreground, "middle", background]
            else:
                return ["foreground", "background"]
                
        except:
            return ["foreground", "background"]
    
    def _create_occupation_map(
        self, 
        image: np.ndarray, 
        faces: List[Tuple[int, int, int, int]]
    ) -> np.ndarray:
        """Create a map showing occupied areas in the image"""
        try:
            height, width = image.shape[:2]
            occupation_map = np.zeros((height, width), dtype=np.uint8)
            
            # Mark face/person regions
            for (x, y, w, h) in faces:
                # Expand to include likely body
                expanded_w = int(w * 2.5)
                expanded_h = int(h * 3.0)
                expanded_x = max(0, x - (expanded_w - w) // 2)
                expanded_y = max(0, y - (expanded_h - h) // 4)
                
                cv2.ellipse(occupation_map,
                           (expanded_x + expanded_w//2, expanded_y + expanded_h//2),
                           (expanded_w//2, expanded_h//2),
                           0, 0, 360, 255, -1)
            
            # Apply Gaussian blur to create soft occupation zones
            occupation_map = cv2.GaussianBlur(occupation_map, (51, 51), 0)
            
            return occupation_map
            
        except Exception as e:
            print(f"⚠️  Occupation map creation failed: {e}")
            return np.zeros(image.shape[:2], dtype=np.uint8)
    
    def _identify_safe_zones(self, occupation_map: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Identify safe zones for friend placement"""
        try:
            if occupation_map is None:
                return []
            
            # Invert occupation map to find free areas
            free_map = cv2.bitwise_not(occupation_map)
            
            # Threshold to binary
            _, binary_free = cv2.threshold(free_map, 128, 255, cv2.THRESH_BINARY)
            
            # Find contours of free areas
            contours, _ = cv2.findContours(binary_free, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            safe_zones = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3000:  # Minimum area for safe placement
                    x, y, w, h = cv2.boundingRect(contour)
                    safe_zones.append((x, y, w, h))
            
            # Sort by area (largest first)
            safe_zones.sort(key=lambda zone: zone[2] * zone[3], reverse=True)
            
            return safe_zones
            
        except Exception as e:
            print(f"⚠️  Safe zone identification failed: {e}")
            return []
    
    def _calculate_placement_region(
        self,
        image: np.ndarray,
        friend_dimensions: Tuple[int, int],
        placement: str,
        composition: Dict[str, Any]
    ) -> Tuple[int, int, int, int]:
        """Calculate optimal placement region for friend"""
        try:
            height, width = image.shape[:2]
            friend_w, friend_h = friend_dimensions
            
            # Get safe zones
            safe_zones = composition.get("safe_zones", [])
            
            if placement == "left":
                # Prefer left side placement
                target_x = width // 6  # Left third
                target_y = height // 3  # Upper third
                
                # Check for safe zones on the left
                for zone in safe_zones:
                    zx, zy, zw, zh = zone
                    if zx < width // 2 and zw >= friend_w and zh >= friend_h:
                        target_x = zx + (zw - friend_w) // 2
                        target_y = zy + (zh - friend_h) // 2
                        break
            
            elif placement == "right":
                # Prefer right side placement
                target_x = width - width // 6 - friend_w  # Right third
                target_y = height // 3  # Upper third
                
                # Check for safe zones on the right
                for zone in safe_zones:
                    zx, zy, zw, zh = zone
                    if zx > width // 2 and zw >= friend_w and zh >= friend_h:
                        target_x = zx + (zw - friend_w) // 2
                        target_y = zy + (zh - friend_h) // 2
                        break
            
            elif placement == "center":
                # Center background placement
                target_x = (width - friend_w) // 2
                target_y = height // 4  # Upper center
                
                # Check for safe zones in center
                for zone in safe_zones:
                    zx, zy, zw, zh = zone
                    if (width // 3 < zx + zw//2 < 2*width // 3 and 
                        zw >= friend_w and zh >= friend_h):
                        target_x = zx + (zw - friend_w) // 2
                        target_y = zy + (zh - friend_h) // 2
                        break
            
            elif placement == "background":
                # Background placement (smaller, further back)
                friend_w = int(friend_w * 0.7)  # Scale down for background
                friend_h = int(friend_h * 0.7)
                target_x = width // 2 - friend_w // 2
                target_y = height // 6  # High in frame
                
                # Use smallest safe zone (likely background)
                if safe_zones:
                    zone = min(safe_zones, key=lambda z: z[2] * z[3])
                    zx, zy, zw, zh = zone
                    if zw >= friend_w and zh >= friend_h:
                        target_x = zx + (zw - friend_w) // 2
                        target_y = zy + (zh - friend_h) // 2
            
            else:
                # Default to right placement
                target_x = width - width // 4 - friend_w
                target_y = height // 3
            
            # Ensure placement is within image bounds
            target_x = max(0, min(target_x, width - friend_w))
            target_y = max(0, min(target_y, height - friend_h))
            
            return (target_x, target_y, friend_w, friend_h)
            
        except Exception as e:
            print(f"⚠️  Placement calculation failed: {e}")
            # Fallback to simple right placement
            target_x = image.shape[1] - friend_dimensions[0] - 50
            target_y = image.shape[0] // 3
            return (target_x, target_y, friend_dimensions[0], friend_dimensions[1])
    
    def _create_integration_mask(
        self,
        image: np.ndarray,
        placement_region: Tuple[int, int, int, int],
        friend_dimensions: Tuple[int, int],
        composition: Dict[str, Any]
    ) -> np.ndarray:
        """Create the actual integration mask"""
        try:
            height, width = image.shape[:2]
            mask = np.zeros((height, width), dtype=np.uint8)
            
            x, y, w, h = placement_region
            
            # Create person-shaped mask (elliptical)
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Ellipse for person shape
            cv2.ellipse(mask, 
                       (center_x, center_y),
                       (w // 3, h // 2),
                       0, 0, 360, 255, -1)
            
            # Apply feathering for smooth edges
            mask = cv2.GaussianBlur(mask, (31, 31), 0)
            
            # Adjust mask based on composition
            occupation_map = composition.get("occupation_map")
            if occupation_map is not None:
                # Reduce mask strength where it overlaps with existing subjects
                overlap_penalty = cv2.bitwise_and(mask, occupation_map)
                mask = cv2.subtract(mask, overlap_penalty // 2)
            
            return mask
            
        except Exception as e:
            print(f"⚠️  Mask creation failed: {e}")
            # Fallback: simple rectangular mask
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            x, y, w, h = placement_region
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
            return cv2.GaussianBlur(mask, (21, 21), 0)
    
    def _refine_mask_with_context(
        self,
        mask: np.ndarray,
        description: str,
        placement_region: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """Refine mask based on friend description"""
        try:
            description_lower = description.lower()
            x, y, w, h = placement_region
            
            # Adjust mask shape based on description
            if "tall" in description_lower:
                # Extend mask vertically
                extended_mask = np.zeros_like(mask)
                cv2.ellipse(extended_mask,
                           (x + w//2, y + h//2),
                           (w//3, int(h//2 * 1.2)),
                           0, 0, 360, 255, -1)
                extended_mask = cv2.GaussianBlur(extended_mask, (31, 31), 0)
                mask = cv2.addWeighted(mask, 0.7, extended_mask, 0.3, 0)
            
            elif "wide" in description_lower or "big" in description_lower:
                # Extend mask horizontally
                extended_mask = np.zeros_like(mask)
                cv2.ellipse(extended_mask,
                           (x + w//2, y + h//2),
                           (int(w//3 * 1.2), h//2),
                           0, 0, 360, 255, -1)
                extended_mask = cv2.GaussianBlur(extended_mask, (31, 31), 0)
                mask = cv2.addWeighted(mask, 0.7, extended_mask, 0.3, 0)
            
            return mask
            
        except Exception as e:
            print(f"⚠️  Context refinement failed: {e}")
            return mask
    
    def _calculate_mask_confidence(
        self,
        mask: np.ndarray,
        placement_region: Tuple[int, int, int, int],
        composition: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the generated mask"""
        try:
            base_confidence = 0.7
            
            # Factor 1: Safe zone utilization
            safe_zones = composition.get("safe_zones", [])
            if safe_zones:
                x, y, w, h = placement_region
                placement_center = (x + w//2, y + h//2)
                
                # Check if placement is within a safe zone
                for zone in safe_zones:
                    zx, zy, zw, zh = zone
                    if (zx <= placement_center[0] <= zx + zw and 
                        zy <= placement_center[1] <= zy + zh):
                        base_confidence += 0.2
                        break
            
            # Factor 2: Mask coverage (not too large, not too small)
            total_pixels = mask.shape[0] * mask.shape[1]
            mask_pixels = np.sum(mask > 0)
            coverage_ratio = mask_pixels / total_pixels
            
            if 0.1 <= coverage_ratio <= 0.3:  # Reasonable coverage
                base_confidence += 0.1
            elif coverage_ratio > 0.5:  # Too much coverage
                base_confidence -= 0.2
            
            # Factor 3: Lighting compatibility
            lighting_quality = composition.get("lighting_analysis", {}).get("lighting_quality", "unknown")
            if lighting_quality == "good":
                base_confidence += 0.1
            elif lighting_quality == "low":
                base_confidence -= 0.1
            
            return min(1.0, max(0.0, base_confidence))
            
        except Exception as e:
            print(f"⚠️  Confidence calculation failed: {e}")
            return 0.5
    
    def save_mask_result(
        self, 
        result: MaskGenerationResult, 
        output_dir: str, 
        filename_prefix: str
    ):
        """Save mask generation results"""
        if not result.success:
            print(f"❌ Cannot save failed mask generation: {result.error_message}")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save mask
        if result.integration_mask is not None:
            mask_path = output_path / f"{filename_prefix}_mask_{timestamp}.png"
            cv2.imwrite(str(mask_path), result.integration_mask)
            print(f"💾 Saved integration mask: {mask_path}")
        
        # Save metadata
        metadata = {
            "success": result.success,
            "confidence": result.confidence,
            "placement_region": result.placement_region,
            "composition_analysis": result.composition_analysis,
            "timestamp": timestamp
        }
        
        metadata_path = output_path / f"{filename_prefix}_mask_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"💾 Saved mask metadata: {metadata_path}")


def main():
    """Demo the mask generation system"""
    generator = IntegrationMaskGenerator()
    
    print("🎭 Integration Mask Generation System Demo")
    print("="*50)
    
    print("📋 Usage:")
    print("  generator = IntegrationMaskGenerator()")
    print("  original = cv2.imread('family_photo.jpg')")
    print("  result = generator.generate_integration_mask(")
    print("      original, (300, 500), 'right', 'woman in blue dress')")
    print("  if result.success:")
    print("      generator.save_mask_result(result, 'output/', 'integration')")
    
    print("\n✅ Mask generation system initialized!")


if __name__ == "__main__":
    main()