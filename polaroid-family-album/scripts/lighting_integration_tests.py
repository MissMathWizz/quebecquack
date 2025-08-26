#!/usr/bin/env python3
"""
Lighting Integration Testing System
Tests friend integration across different lighting conditions and photo compositions.
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime
import asyncio
import requests
from PIL import Image, ImageEnhance, ImageFilter
from dataclasses import dataclass
from friend_extraction_processor import FriendExtractionProcessor
from mask_generation_system import IntegrationMaskGenerator


@dataclass
class LightingTestScenario:
    """Test scenario for lighting integration"""
    name: str
    description: str
    lighting_conditions: Dict[str, Any]
    expected_challenges: List[str]
    success_criteria: Dict[str, float]


@dataclass
class IntegrationTestResult:
    """Result from integration testing"""
    scenario_name: str
    success: bool
    quality_score: float
    lighting_match_score: float
    composition_score: float
    realism_score: float
    processing_time: float
    error_message: str = ""


class LightingIntegrationTester:
    def __init__(self):
        self.extractor = FriendExtractionProcessor()
        self.mask_generator = IntegrationMaskGenerator()
        self.test_scenarios = self._create_test_scenarios()
        
    def _create_test_scenarios(self) -> List[LightingTestScenario]:
        """Create comprehensive lighting test scenarios"""
        return [
            LightingTestScenario(
                name="bright_daylight",
                description="Bright outdoor daylight with strong shadows",
                lighting_conditions={
                    "brightness": 180,
                    "contrast": 0.8,
                    "color_temperature": 0.9,  # Slightly warm
                    "shadow_strength": 0.7,
                    "lighting_direction": "top",
                    "lighting_type": "direct"
                },
                expected_challenges=[
                    "Strong shadow casting",
                    "High contrast preservation",
                    "Natural shadow direction matching"
                ],
                success_criteria={
                    "lighting_match": 0.8,
                    "shadow_consistency": 0.7,
                    "overall_realism": 0.75
                }
            ),
            
            LightingTestScenario(
                name="overcast_outdoor",
                description="Overcast outdoor lighting with soft shadows",
                lighting_conditions={
                    "brightness": 140,
                    "contrast": 0.4,
                    "color_temperature": 1.1,  # Slightly cool
                    "shadow_strength": 0.2,
                    "lighting_direction": "diffuse",
                    "lighting_type": "soft"
                },
                expected_challenges=[
                    "Soft shadow generation",
                    "Color temperature adjustment",
                    "Low contrast environment"
                ],
                success_criteria={
                    "lighting_match": 0.85,
                    "color_harmony": 0.8,
                    "overall_realism": 0.8
                }
            ),
            
            LightingTestScenario(
                name="golden_hour",
                description="Golden hour with warm directional lighting",
                lighting_conditions={
                    "brightness": 160,
                    "contrast": 0.6,
                    "color_temperature": 0.7,  # Very warm
                    "shadow_strength": 0.5,
                    "lighting_direction": "left",
                    "lighting_type": "warm_direct"
                },
                expected_challenges=[
                    "Warm color cast matching",
                    "Directional shadow consistency",
                    "Golden tone preservation"
                ],
                success_criteria={
                    "lighting_match": 0.7,
                    "color_harmony": 0.9,
                    "shadow_consistency": 0.8,
                    "overall_realism": 0.8
                }
            ),
            
            LightingTestScenario(
                name="indoor_mixed",
                description="Mixed indoor lighting (window + artificial)",
                lighting_conditions={
                    "brightness": 120,
                    "contrast": 0.5,
                    "color_temperature": 1.0,  # Mixed
                    "shadow_strength": 0.4,
                    "lighting_direction": "mixed",
                    "lighting_type": "mixed"
                },
                expected_challenges=[
                    "Multiple light source simulation",
                    "Color temperature balance",
                    "Complex shadow patterns"
                ],
                success_criteria={
                    "lighting_match": 0.6,
                    "color_harmony": 0.7,
                    "overall_realism": 0.65
                }
            ),
            
            LightingTestScenario(
                name="low_light_indoor",
                description="Low light indoor with artificial lighting",
                lighting_conditions={
                    "brightness": 80,
                    "contrast": 0.3,
                    "color_temperature": 0.8,  # Warm artificial
                    "shadow_strength": 0.6,
                    "lighting_direction": "center",
                    "lighting_type": "artificial"
                },
                expected_challenges=[
                    "Low light noise management",
                    "Artificial light color cast",
                    "Detail preservation in shadows"
                ],
                success_criteria={
                    "lighting_match": 0.7,
                    "noise_management": 0.6,
                    "overall_realism": 0.6
                }
            ),
            
            LightingTestScenario(
                name="backlit_silhouette",
                description="Backlit scenario with strong rim lighting",
                lighting_conditions={
                    "brightness": 200,
                    "contrast": 0.9,
                    "color_temperature": 1.0,
                    "shadow_strength": 0.9,
                    "lighting_direction": "back",
                    "lighting_type": "backlit"
                },
                expected_challenges=[
                    "Rim light simulation",
                    "High dynamic range handling",
                    "Silhouette edge definition"
                ],
                success_criteria={
                    "lighting_match": 0.6,
                    "rim_light_effect": 0.7,
                    "overall_realism": 0.65
                }
            )
        ]
    
    def create_synthetic_test_images(self) -> Dict[str, np.ndarray]:
        """Create synthetic test images for different lighting scenarios"""
        test_images = {}
        
        # Base image dimensions
        height, width = 600, 800
        
        for scenario in self.test_scenarios:
            print(f"🎨 Creating synthetic test image for: {scenario.name}")
            
            # Create base image
            base_image = np.ones((height, width, 3), dtype=np.uint8) * 128
            
            # Apply lighting characteristics
            lighting = scenario.lighting_conditions
            
            # Brightness adjustment
            brightness_factor = lighting["brightness"] / 128
            base_image = (base_image * brightness_factor).astype(np.uint8)
            
            # Color temperature adjustment
            color_temp = lighting["color_temperature"]
            if color_temp < 1.0:  # Warm
                base_image[:, :, 0] = np.clip(base_image[:, :, 0] * 0.9, 0, 255)  # Reduce blue
                base_image[:, :, 2] = np.clip(base_image[:, :, 2] * 1.1, 0, 255)  # Enhance red
            elif color_temp > 1.0:  # Cool
                base_image[:, :, 0] = np.clip(base_image[:, :, 0] * 1.1, 0, 255)  # Enhance blue
                base_image[:, :, 2] = np.clip(base_image[:, :, 2] * 0.9, 0, 255)  # Reduce red
            
            # Add gradient based on lighting direction
            direction = lighting["lighting_direction"]
            if direction == "top":
                gradient = np.linspace(1.2, 0.8, height)
                for i in range(height):
                    base_image[i, :] = np.clip(base_image[i, :] * gradient[i], 0, 255)
            elif direction == "left":
                gradient = np.linspace(1.2, 0.8, width)
                for j in range(width):
                    base_image[:, j] = np.clip(base_image[:, j] * gradient[j], 0, 255)
            elif direction == "right":
                gradient = np.linspace(0.8, 1.2, width)
                for j in range(width):
                    base_image[:, j] = np.clip(base_image[:, j] * gradient[j], 0, 255)
            
            # Add mock subjects (simple rectangles representing people)
            # Main subject
            cv2.rectangle(base_image, (200, 200), (300, 500), (120, 100, 80), -1)
            # Secondary subject
            cv2.rectangle(base_image, (450, 180), (530, 480), (100, 120, 90), -1)
            
            # Add noise for realism
            noise = np.random.normal(0, 5, base_image.shape).astype(np.int16)
            base_image = np.clip(base_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
            test_images[scenario.name] = base_image
        
        return test_images
    
    def create_synthetic_friend_images(self) -> Dict[str, np.ndarray]:
        """Create synthetic friend images with different characteristics"""
        friend_images = {}
        
        # Base friend dimensions
        height, width = 400, 300
        
        lighting_variations = [
            ("bright_friend", {"brightness": 180, "color_temp": 0.9}),
            ("dim_friend", {"brightness": 100, "color_temp": 1.1}),
            ("warm_friend", {"brightness": 140, "color_temp": 0.7}),
            ("cool_friend", {"brightness": 140, "color_temp": 1.3}),
            ("neutral_friend", {"brightness": 128, "color_temp": 1.0})
        ]
        
        for name, characteristics in lighting_variations:
            # Create base friend image
            friend_image = np.ones((height, width, 3), dtype=np.uint8) * 120
            
            # Add person shape (ellipse)
            cv2.ellipse(friend_image, (width//2, height//2), (width//3, height//2), 
                       0, 0, 360, (110, 90, 75), -1)
            
            # Apply lighting characteristics
            brightness_factor = characteristics["brightness"] / 128
            friend_image = (friend_image * brightness_factor).astype(np.uint8)
            
            # Color temperature
            color_temp = characteristics["color_temp"]
            if color_temp < 1.0:  # Warm
                friend_image[:, :, 0] = np.clip(friend_image[:, :, 0] * 0.9, 0, 255)
                friend_image[:, :, 2] = np.clip(friend_image[:, :, 2] * 1.1, 0, 255)
            elif color_temp > 1.0:  # Cool
                friend_image[:, :, 0] = np.clip(friend_image[:, :, 0] * 1.1, 0, 255)
                friend_image[:, :, 2] = np.clip(friend_image[:, :, 2] * 0.9, 0, 255)
            
            friend_images[name] = friend_image
        
        return friend_images
    
    async def run_lighting_integration_tests(self, save_results: bool = True) -> List[IntegrationTestResult]:
        """Run comprehensive lighting integration tests"""
        print("🔬 Starting Lighting Integration Tests")
        print("="*50)
        
        # Create test images
        test_images = self.create_synthetic_test_images()
        friend_images = self.create_synthetic_friend_images()
        
        results = []
        
        for scenario in self.test_scenarios:
            print(f"\n🧪 Testing scenario: {scenario.name}")
            print(f"   Description: {scenario.description}")
            
            original_image = test_images[scenario.name]
            
            # Test with different friend lighting variations
            for friend_name, friend_image in friend_images.items():
                start_time = datetime.now()
                
                try:
                    # Extract friend
                    extraction_result = self.extractor.extract_friend_from_photo_array(
                        friend_image, f"person with {friend_name} lighting"
                    )
                    
                    if not extraction_result.success:
                        results.append(IntegrationTestResult(
                            scenario_name=f"{scenario.name}_{friend_name}",
                            success=False,
                            quality_score=0.0,
                            lighting_match_score=0.0,
                            composition_score=0.0,
                            realism_score=0.0,
                            processing_time=0.0,
                            error_message=f"Friend extraction failed: {extraction_result.error_message}"
                        ))
                        continue
                    
                    # Generate integration mask
                    friend_h, friend_w = friend_image.shape[:2]
                    mask_result = self.mask_generator.generate_integration_mask(
                        original_image, (friend_w, friend_h), "right", f"person with {friend_name} lighting"
                    )
                    
                    if not mask_result.success:
                        results.append(IntegrationTestResult(
                            scenario_name=f"{scenario.name}_{friend_name}",
                            success=False,
                            quality_score=0.0,
                            lighting_match_score=0.0,
                            composition_score=0.0,
                            realism_score=0.0,
                            processing_time=0.0,
                            error_message=f"Mask generation failed: {mask_result.error_message}"
                        ))
                        continue
                    
                    # Simulate integration (in real implementation, would use inpainting)
                    integrated_image = self._simulate_integration(
                        original_image, extraction_result, mask_result, scenario.lighting_conditions
                    )
                    
                    # Evaluate integration quality
                    evaluation = self._evaluate_integration_quality(
                        integrated_image, scenario, extraction_result, mask_result
                    )
                    
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    result = IntegrationTestResult(
                        scenario_name=f"{scenario.name}_{friend_name}",
                        success=True,
                        quality_score=evaluation["quality_score"],
                        lighting_match_score=evaluation["lighting_match_score"],
                        composition_score=evaluation["composition_score"],
                        realism_score=evaluation["realism_score"],
                        processing_time=processing_time
                    )
                    
                    results.append(result)
                    
                    # Save test results if requested
                    if save_results:
                        self._save_test_result(
                            scenario.name, friend_name, original_image, 
                            friend_image, integrated_image, result, evaluation
                        )
                    
                    print(f"   ✅ {friend_name}: Quality={evaluation['quality_score']:.2f}, "
                          f"Lighting={evaluation['lighting_match_score']:.2f}")
                    
                except Exception as e:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    results.append(IntegrationTestResult(
                        scenario_name=f"{scenario.name}_{friend_name}",
                        success=False,
                        quality_score=0.0,
                        lighting_match_score=0.0,
                        composition_score=0.0,
                        realism_score=0.0,
                        processing_time=processing_time,
                        error_message=str(e)
                    ))
                    print(f"   ❌ {friend_name}: {str(e)}")
        
        # Generate comprehensive report
        if save_results:
            self._generate_test_report(results)
        
        return results
    
    def extract_friend_from_photo_array(self, image_array: np.ndarray, description: str):
        """Extract friend from numpy array (mock implementation)"""
        try:
            # Simulate extraction process
            height, width = image_array.shape[:2]
            
            # Find the main subject (largest non-background region)
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            
            # Simple thresholding to find subject
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Use largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Extract region
                extracted = image_array[y:y+h, x:x+w]
                
                # Create simple mask
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.ellipse(mask, (w//2, h//2), (w//3, h//2), 0, 0, 360, 255, -1)
                mask = cv2.GaussianBlur(mask, (15, 15), 0)
                
                # Analyze lighting
                lighting_analysis = {
                    "brightness": float(np.mean(gray)),
                    "contrast": float(np.std(gray)),
                    "color_temperature": 1.0
                }
                
                return type('ExtractionResult', (), {
                    'success': True,
                    'extracted_image': extracted,
                    'mask': mask,
                    'bounding_box': (x, y, w, h),
                    'confidence': 0.8,
                    'lighting_analysis': lighting_analysis
                })()
            
            else:
                return type('ExtractionResult', (), {
                    'success': False,
                    'error_message': 'No subject found in image'
                })()
                
        except Exception as e:
            return type('ExtractionResult', (), {
                'success': False,
                'error_message': str(e)
            })()
    
    def _simulate_integration(self, original, extraction_result, mask_result, target_lighting):
        """Simulate the integration process"""
        try:
            integrated = original.copy()
            
            if mask_result.placement_region:
                x, y, w, h = mask_result.placement_region
                
                # Resize friend to fit placement
                friend_resized = cv2.resize(extraction_result.extracted_image, (w, h))
                
                # Apply lighting adjustments
                friend_adjusted = self._adjust_friend_lighting(friend_resized, target_lighting)
                
                # Blend into original using mask
                if mask_result.integration_mask is not None:
                    mask_region = mask_result.integration_mask[y:y+h, x:x+w]
                    if mask_region.shape == friend_adjusted.shape[:2]:
                        # Normalize mask
                        mask_norm = mask_region.astype(np.float32) / 255.0
                        
                        # Blend
                        for c in range(3):
                            integrated[y:y+h, x:x+w, c] = (
                                integrated[y:y+h, x:x+w, c] * (1 - mask_norm) +
                                friend_adjusted[:, :, c] * mask_norm
                            ).astype(np.uint8)
            
            return integrated
            
        except Exception as e:
            print(f"⚠️  Integration simulation failed: {e}")
            return original
    
    def _adjust_friend_lighting(self, friend_image, target_lighting):
        """Adjust friend image lighting to match target conditions"""
        try:
            adjusted = friend_image.copy().astype(np.float32)
            
            # Brightness adjustment
            current_brightness = np.mean(cv2.cvtColor(friend_image, cv2.COLOR_BGR2GRAY))
            target_brightness = target_lighting.get("brightness", 128)
            brightness_ratio = target_brightness / max(current_brightness, 1)
            
            adjusted = adjusted * brightness_ratio
            
            # Color temperature adjustment
            target_temp = target_lighting.get("color_temperature", 1.0)
            if target_temp < 1.0:  # Warm
                adjusted[:, :, 0] *= 0.9  # Reduce blue
                adjusted[:, :, 2] *= 1.1  # Enhance red
            elif target_temp > 1.0:  # Cool
                adjusted[:, :, 0] *= 1.1  # Enhance blue
                adjusted[:, :, 2] *= 0.9  # Reduce red
            
            return np.clip(adjusted, 0, 255).astype(np.uint8)
            
        except Exception as e:
            print(f"⚠️  Lighting adjustment failed: {e}")
            return friend_image
    
    def _evaluate_integration_quality(self, integrated_image, scenario, extraction_result, mask_result):
        """Evaluate the quality of integration"""
        try:
            # Quality metrics
            quality_score = 0.7  # Base score
            
            # Lighting match evaluation
            lighting_match_score = self._evaluate_lighting_match(
                integrated_image, scenario.lighting_conditions
            )
            
            # Composition evaluation
            composition_score = mask_result.confidence if mask_result else 0.5
            
            # Realism evaluation (simplified)
            realism_score = (extraction_result.confidence + lighting_match_score) / 2
            
            # Overall quality
            quality_score = (lighting_match_score * 0.4 + 
                           composition_score * 0.3 + 
                           realism_score * 0.3)
            
            return {
                "quality_score": quality_score,
                "lighting_match_score": lighting_match_score,
                "composition_score": composition_score,
                "realism_score": realism_score
            }
            
        except Exception as e:
            print(f"⚠️  Quality evaluation failed: {e}")
            return {
                "quality_score": 0.5,
                "lighting_match_score": 0.5,
                "composition_score": 0.5,
                "realism_score": 0.5
            }
    
    def _evaluate_lighting_match(self, image, target_lighting):
        """Evaluate how well the integrated image matches target lighting"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check brightness match
            current_brightness = np.mean(gray)
            target_brightness = target_lighting.get("brightness", 128)
            brightness_diff = abs(current_brightness - target_brightness) / 255
            brightness_score = max(0, 1 - brightness_diff * 2)
            
            # Check contrast match
            current_contrast = np.std(gray) / 255
            target_contrast = target_lighting.get("contrast", 0.5)
            contrast_diff = abs(current_contrast - target_contrast)
            contrast_score = max(0, 1 - contrast_diff * 2)
            
            # Overall lighting match
            lighting_score = (brightness_score + contrast_score) / 2
            
            return lighting_score
            
        except Exception as e:
            print(f"⚠️  Lighting evaluation failed: {e}")
            return 0.5
    
    def _save_test_result(self, scenario_name, friend_name, original, friend, integrated, result, evaluation):
        """Save test results to disk"""
        try:
            output_dir = Path("validation/lighting_tests")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = f"{scenario_name}_{friend_name}_{timestamp}"
            
            # Save images
            cv2.imwrite(str(output_dir / f"{test_name}_original.png"), original)
            cv2.imwrite(str(output_dir / f"{test_name}_friend.png"), friend)
            cv2.imwrite(str(output_dir / f"{test_name}_integrated.png"), integrated)
            
            # Save metadata
            metadata = {
                "scenario": scenario_name,
                "friend_variant": friend_name,
                "timestamp": timestamp,
                "result": {
                    "success": result.success,
                    "quality_score": result.quality_score,
                    "lighting_match_score": result.lighting_match_score,
                    "composition_score": result.composition_score,
                    "realism_score": result.realism_score,
                    "processing_time": result.processing_time,
                    "error_message": result.error_message
                },
                "evaluation": evaluation
            }
            
            with open(output_dir / f"{test_name}_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to save test result: {e}")
    
    def _generate_test_report(self, results):
        """Generate comprehensive test report"""
        try:
            output_dir = Path("validation/lighting_tests")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = output_dir / f"lighting_integration_report_{timestamp}.md"
            
            # Calculate summary statistics
            total_tests = len(results)
            successful_tests = len([r for r in results if r.success])
            avg_quality = np.mean([r.quality_score for r in results if r.success])
            avg_lighting_match = np.mean([r.lighting_match_score for r in results if r.success])
            
            with open(report_path, 'w') as f:
                f.write("# Lighting Integration Test Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Executive Summary
                f.write("## Executive Summary\n\n")
                f.write(f"- **Total Tests:** {total_tests}\n")
                f.write(f"- **Successful:** {successful_tests} ({successful_tests/total_tests:.1%})\n")
                f.write(f"- **Average Quality Score:** {avg_quality:.3f}\n")
                f.write(f"- **Average Lighting Match:** {avg_lighting_match:.3f}\n\n")
                
                # Scenario Performance
                f.write("## Scenario Performance\n\n")
                scenarios = {}
                for result in results:
                    scenario_base = result.scenario_name.split('_')[0]
                    if scenario_base not in scenarios:
                        scenarios[scenario_base] = []
                    scenarios[scenario_base].append(result)
                
                for scenario, scenario_results in scenarios.items():
                    successful = [r for r in scenario_results if r.success]
                    if successful:
                        avg_quality = np.mean([r.quality_score for r in successful])
                        avg_lighting = np.mean([r.lighting_match_score for r in successful])
                        f.write(f"### {scenario.title()}\n")
                        f.write(f"- Success Rate: {len(successful)}/{len(scenario_results)} ({len(successful)/len(scenario_results):.1%})\n")
                        f.write(f"- Average Quality: {avg_quality:.3f}\n")
                        f.write(f"- Average Lighting Match: {avg_lighting:.3f}\n\n")
                
                # Detailed Results
                f.write("## Detailed Results\n\n")
                f.write("| Test | Success | Quality | Lighting | Composition | Realism | Time(s) |\n")
                f.write("|------|---------|---------|----------|-------------|---------|----------|\n")
                
                for result in results:
                    status = "✅" if result.success else "❌"
                    f.write(f"| {result.scenario_name} | {status} | {result.quality_score:.3f} | "
                           f"{result.lighting_match_score:.3f} | {result.composition_score:.3f} | "
                           f"{result.realism_score:.3f} | {result.processing_time:.2f} |\n")
                
                # Recommendations
                f.write("\n## Recommendations\n\n")
                
                failed_tests = [r for r in results if not r.success]
                if failed_tests:
                    f.write(f"- **{len(failed_tests)} tests failed** - investigate error patterns\n")
                
                low_quality = [r for r in results if r.success and r.quality_score < 0.6]
                if low_quality:
                    f.write(f"- **{len(low_quality)} tests show low quality** - improve integration algorithms\n")
                
                low_lighting = [r for r in results if r.success and r.lighting_match_score < 0.6]
                if low_lighting:
                    f.write(f"- **{len(low_lighting)} tests show poor lighting match** - enhance lighting adjustment\n")
            
            print(f"📄 Test report generated: {report_path}")
            
        except Exception as e:
            print(f"⚠️  Report generation failed: {e}")


async def main():
    """Run lighting integration tests"""
    tester = LightingIntegrationTester()
    
    print("🔬 Starting Comprehensive Lighting Integration Tests")
    print("="*60)
    
    # Run tests
    results = await tester.run_lighting_integration_tests(save_results=True)
    
    # Summary
    successful = len([r for r in results if r.success])
    total = len(results)
    
    print(f"\n📊 Test Summary:")
    print(f"   Total Tests: {total}")
    print(f"   Successful: {successful} ({successful/total:.1%})")
    
    if successful > 0:
        avg_quality = np.mean([r.quality_score for r in results if r.success])
        avg_lighting = np.mean([r.lighting_match_score for r in results if r.success])
        print(f"   Average Quality: {avg_quality:.3f}")
        print(f"   Average Lighting Match: {avg_lighting:.3f}")
    
    print(f"\n✅ Lighting integration tests complete!")
    print(f"   Check validation/lighting_tests/ for detailed results")


if __name__ == "__main__":
    asyncio.run(main())