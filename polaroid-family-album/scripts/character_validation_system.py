#!/usr/bin/env python3
"""
Character Validation System with Face Similarity Scoring
Analyzes face consistency across generated photos of Ferwanda and Ferwando.
"""

import os
import json
import numpy as np
import cv2
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import face_recognition
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass


@dataclass
class FaceAnalysis:
    """Face analysis result data structure"""
    image_path: str
    character: str
    location: str
    age_group: str
    face_encodings: List[np.ndarray]
    face_locations: List[Tuple[int, int, int, int]]
    confidence_score: float
    face_detected: bool


class CharacterValidationSystem:
    def __init__(self, validation_dir: str = "validation"):
        self.validation_dir = Path(validation_dir)
        self.results_dir = self.validation_dir / "analysis_results"
        self.images_dir = self.validation_dir / "test_images"
        
        # Create directories
        for dir_path in [self.results_dir, self.images_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Face recognition settings
        self.face_model = "large"  # Use large model for better accuracy
        self.similarity_threshold = 0.6  # Cosine similarity threshold
        
        # Character reference encodings (will be set from reference images)
        self.reference_encodings = {
            "ferwanda": [],
            "ferwando": []
        }
        
    def download_images(self, generation_results: List[Dict[str, Any]]) -> List[str]:
        """Download generated images for analysis"""
        print("📥 Downloading generated images...")
        
        downloaded_paths = []
        
        for result in generation_results:
            if not result.get("success", False):
                continue
                
            try:
                image_url = result["image_url"]
                filename = result["filename"]
                local_path = self.images_dir / filename
                
                # Download image
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_paths.append(str(local_path))
                print(f"✅ Downloaded: {filename}")
                
            except Exception as e:
                print(f"❌ Failed to download {result.get('filename', 'unknown')}: {e}")
        
        print(f"📁 Downloaded {len(downloaded_paths)} images")
        return downloaded_paths
    
    def load_reference_images(self, reference_dir: str):
        """Load reference images to establish character baselines"""
        print("📚 Loading reference images...")
        
        ref_path = Path(reference_dir)
        if not ref_path.exists():
            print(f"⚠️  Reference directory not found: {reference_dir}")
            return
        
        for character in ["ferwanda", "ferwando"]:
            character_dir = ref_path / character
            if not character_dir.exists():
                continue
                
            encodings = []
            for img_file in character_dir.glob("*.{jpg,jpeg,png}"):
                try:
                    image = face_recognition.load_image_file(str(img_file))
                    face_encodings = face_recognition.face_encodings(
                        image, model=self.face_model
                    )
                    
                    if face_encodings:
                        encodings.extend(face_encodings)
                        print(f"✅ Loaded reference: {img_file.name}")
                    
                except Exception as e:
                    print(f"❌ Error loading {img_file}: {e}")
            
            self.reference_encodings[character] = encodings
            print(f"📊 {character}: {len(encodings)} reference encodings")
    
    def analyze_face(self, image_path: str, metadata: Dict[str, Any]) -> FaceAnalysis:
        """Analyze faces in a single image"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect faces
            face_locations = face_recognition.face_locations(
                image, model=self.face_model
            )
            face_encodings = face_recognition.face_encodings(
                image, face_locations, model=self.face_model
            )
            
            # Calculate confidence score based on face detection
            face_detected = len(face_encodings) > 0
            
            if face_detected:
                # For multiple faces, use the largest face as primary
                if len(face_encodings) > 1:
                    largest_face_idx = self._get_largest_face_index(face_locations)
                    primary_encoding = [face_encodings[largest_face_idx]]
                    primary_location = [face_locations[largest_face_idx]]
                else:
                    primary_encoding = face_encodings
                    primary_location = face_locations
                
                confidence_score = self._calculate_confidence_score(
                    primary_encoding[0], metadata["character"]
                )
            else:
                primary_encoding = []
                primary_location = []
                confidence_score = 0.0
            
            return FaceAnalysis(
                image_path=image_path,
                character=metadata["character"],
                location=metadata["location"],
                age_group=metadata["age"],
                face_encodings=primary_encoding,
                face_locations=primary_location,
                confidence_score=confidence_score,
                face_detected=face_detected
            )
            
        except Exception as e:
            print(f"❌ Error analyzing {image_path}: {e}")
            return FaceAnalysis(
                image_path=image_path,
                character=metadata["character"],
                location=metadata["location"], 
                age_group=metadata["age"],
                face_encodings=[],
                face_locations=[],
                confidence_score=0.0,
                face_detected=False
            )
    
    def _get_largest_face_index(self, face_locations: List[Tuple]) -> int:
        """Get index of largest face"""
        areas = []
        for (top, right, bottom, left) in face_locations:
            area = (bottom - top) * (right - left)
            areas.append(area)
        return np.argmax(areas)
    
    def _calculate_confidence_score(self, face_encoding: np.ndarray, character: str) -> float:
        """Calculate confidence score against reference encodings"""
        if character not in self.reference_encodings or not self.reference_encodings[character]:
            return 0.5  # Default score when no reference available
        
        # Compare against all reference encodings
        similarities = []
        for ref_encoding in self.reference_encodings[character]:
            similarity = cosine_similarity([face_encoding], [ref_encoding])[0][0]
            similarities.append(similarity)
        
        # Return best match
        return max(similarities) if similarities else 0.0
    
    def analyze_all_images(self, image_paths: List[str], generation_results: List[Dict[str, Any]]) -> List[FaceAnalysis]:
        """Analyze all generated images"""
        print("🔍 Analyzing face consistency across all images...")
        
        analyses = []
        
        for image_path in image_paths:
            # Find corresponding metadata
            filename = Path(image_path).name
            metadata = None
            
            for result in generation_results:
                if result.get("filename") == filename and result.get("success", False):
                    metadata = result["scenario"]
                    break
            
            if metadata:
                analysis = self.analyze_face(image_path, metadata)
                analyses.append(analysis)
                print(f"✅ Analyzed: {filename} (confidence: {analysis.confidence_score:.3f})")
            else:
                print(f"⚠️  No metadata found for: {filename}")
        
        return analyses
    
    def calculate_consistency_metrics(self, analyses: List[FaceAnalysis]) -> Dict[str, Any]:
        """Calculate character consistency metrics"""
        print("📊 Calculating consistency metrics...")
        
        metrics = {
            "overall_stats": {},
            "character_stats": {},
            "location_stats": {},
            "age_stats": {},
            "similarity_matrix": {}
        }
        
        # Overall statistics
        total_images = len(analyses)
        faces_detected = len([a for a in analyses if a.face_detected])
        avg_confidence = np.mean([a.confidence_score for a in analyses if a.face_detected])
        
        metrics["overall_stats"] = {
            "total_images": total_images,
            "faces_detected": faces_detected,
            "detection_rate": faces_detected / total_images if total_images > 0 else 0,
            "average_confidence": float(avg_confidence) if faces_detected > 0 else 0,
            "high_confidence_count": len([a for a in analyses if a.confidence_score > 0.8]),
            "low_confidence_count": len([a for a in analyses if a.confidence_score < 0.4])
        }
        
        # Character-specific statistics
        for character in ["ferwanda", "ferwando", "both"]:
            char_analyses = [a for a in analyses if a.character == character]
            if char_analyses:
                char_confidences = [a.confidence_score for a in char_analyses if a.face_detected]
                metrics["character_stats"][character] = {
                    "total_images": len(char_analyses),
                    "faces_detected": len([a for a in char_analyses if a.face_detected]),
                    "average_confidence": float(np.mean(char_confidences)) if char_confidences else 0,
                    "std_confidence": float(np.std(char_confidences)) if char_confidences else 0,
                    "min_confidence": float(np.min(char_confidences)) if char_confidences else 0,
                    "max_confidence": float(np.max(char_confidences)) if char_confidences else 0
                }
        
        # Location-specific statistics
        locations = set(a.location for a in analyses)
        for location in locations:
            loc_analyses = [a for a in analyses if a.location == location]
            loc_confidences = [a.confidence_score for a in loc_analyses if a.face_detected]
            metrics["location_stats"][location] = {
                "total_images": len(loc_analyses),
                "faces_detected": len([a for a in loc_analyses if a.face_detected]),
                "average_confidence": float(np.mean(loc_confidences)) if loc_confidences else 0
            }
        
        # Age group statistics
        age_groups = set(a.age_group for a in analyses)
        for age_group in age_groups:
            age_analyses = [a for a in analyses if a.age_group == age_group]
            age_confidences = [a.confidence_score for a in age_analyses if a.face_detected]
            metrics["age_stats"][age_group] = {
                "total_images": len(age_analyses),
                "faces_detected": len([a for a in age_analyses if a.face_detected]),
                "average_confidence": float(np.mean(age_confidences)) if age_confidences else 0
            }
        
        return metrics
    
    def generate_visualizations(self, analyses: List[FaceAnalysis], metrics: Dict[str, Any]):
        """Generate visualization charts"""
        print("📈 Generating visualization charts...")
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Character Consistency Analysis', fontsize=16, fontweight='bold')
        
        # 1. Confidence scores by character
        characters = [a.character for a in analyses if a.face_detected]
        confidences = [a.confidence_score for a in analyses if a.face_detected]
        
        ax1 = axes[0, 0]
        char_data = {}
        for char, conf in zip(characters, confidences):
            if char not in char_data:
                char_data[char] = []
            char_data[char].append(conf)
        
        for char, confs in char_data.items():
            ax1.hist(confs, alpha=0.7, label=char, bins=10)
        ax1.set_xlabel('Confidence Score')
        ax1.set_ylabel('Count')
        ax1.set_title('Confidence Score Distribution by Character')
        ax1.legend()
        
        # 2. Detection rate by location
        ax2 = axes[0, 1]
        locations = list(metrics["location_stats"].keys())
        detection_rates = [
            metrics["location_stats"][loc]["faces_detected"] / metrics["location_stats"][loc]["total_images"]
            for loc in locations
        ]
        ax2.bar(locations, detection_rates)
        ax2.set_ylabel('Detection Rate')
        ax2.set_title('Face Detection Rate by Location')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Confidence by location and character
        ax3 = axes[1, 0]
        location_char_data = {}
        for analysis in analyses:
            if not analysis.face_detected:
                continue
            key = f"{analysis.location}_{analysis.character}"
            if key not in location_char_data:
                location_char_data[key] = []
            location_char_data[key].append(analysis.confidence_score)
        
        keys = list(location_char_data.keys())
        values = [np.mean(location_char_data[key]) for key in keys]
        ax3.bar(range(len(keys)), values)
        ax3.set_xticks(range(len(keys)))
        ax3.set_xticklabels(keys, rotation=45, ha='right')
        ax3.set_ylabel('Average Confidence')
        ax3.set_title('Average Confidence by Location and Character')
        
        # 4. Summary statistics
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
        Overall Statistics:
        • Total Images: {metrics['overall_stats']['total_images']}
        • Detection Rate: {metrics['overall_stats']['detection_rate']:.1%}
        • Average Confidence: {metrics['overall_stats']['average_confidence']:.3f}
        • High Confidence (>0.8): {metrics['overall_stats']['high_confidence_count']}
        • Low Confidence (<0.4): {metrics['overall_stats']['low_confidence_count']}
        
        Character Performance:
        """
        
        for char, stats in metrics['character_stats'].items():
            summary_text += f"• {char.title()}: {stats['average_confidence']:.3f} ± {stats['std_confidence']:.3f}\n"
        
        ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, 
                verticalalignment='top', fontsize=10, fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save visualization
        viz_path = self.results_dir / f"consistency_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved to: {viz_path}")
        
        return viz_path
    
    def generate_report(self, analyses: List[FaceAnalysis], metrics: Dict[str, Any]) -> str:
        """Generate comprehensive consistency report"""
        print("📝 Generating consistency report...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.results_dir / f"consistency_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write("# Character Consistency Validation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            overall = metrics['overall_stats']
            f.write(f"- **Total Images Analyzed:** {overall['total_images']}\n")
            f.write(f"- **Face Detection Rate:** {overall['detection_rate']:.1%}\n")
            f.write(f"- **Average Confidence Score:** {overall['average_confidence']:.3f}\n")
            f.write(f"- **High Confidence Images:** {overall['high_confidence_count']} (>{0.8})\n")
            f.write(f"- **Low Confidence Images:** {overall['low_confidence_count']} (<{0.4})\n\n")
            
            # Character Analysis
            f.write("## Character-Specific Analysis\n\n")
            for char, stats in metrics['character_stats'].items():
                f.write(f"### {char.title()}\n")
                f.write(f"- Images: {stats['total_images']}\n")
                f.write(f"- Detection Rate: {stats['faces_detected']}/{stats['total_images']} ({stats['faces_detected']/stats['total_images']:.1%})\n")
                f.write(f"- Average Confidence: {stats['average_confidence']:.3f} ± {stats['std_confidence']:.3f}\n")
                f.write(f"- Confidence Range: {stats['min_confidence']:.3f} - {stats['max_confidence']:.3f}\n\n")
            
            # Location Analysis
            f.write("## Location-Specific Analysis\n\n")
            for loc, stats in metrics['location_stats'].items():
                f.write(f"### {loc.replace('_', ' ').title()}\n")
                f.write(f"- Images: {stats['total_images']}\n")
                f.write(f"- Detection Rate: {stats['faces_detected']}/{stats['total_images']} ({stats['faces_detected']/stats['total_images']:.1%})\n")
                f.write(f"- Average Confidence: {stats['average_confidence']:.3f}\n\n")
            
            # Detailed Results
            f.write("## Detailed Results\n\n")
            f.write("| Image | Character | Location | Age Group | Face Detected | Confidence |\n")
            f.write("|-------|-----------|----------|-----------|---------------|------------|\n")
            
            for analysis in analyses:
                filename = Path(analysis.image_path).name
                f.write(f"| {filename} | {analysis.character} | {analysis.location} | {analysis.age_group} | {analysis.face_detected} | {analysis.confidence_score:.3f} |\n")
            
            # Recommendations
            f.write("\n## Recommendations\n\n")
            
            if overall['detection_rate'] < 0.8:
                f.write("- **Low Detection Rate:** Consider improving prompt specificity or adjusting model parameters.\n")
            
            if overall['average_confidence'] < 0.6:
                f.write("- **Low Confidence Scores:** May need more reference images or LoRA retraining.\n")
            
            # Find worst performing scenarios
            low_conf_analyses = [a for a in analyses if a.confidence_score < 0.4]
            if low_conf_analyses:
                f.write("- **Low Confidence Scenarios:**\n")
                for analysis in low_conf_analyses[:5]:  # Top 5 worst
                    f.write(f"  - {analysis.character} at {analysis.location} ({analysis.confidence_score:.3f})\n")
        
        print(f"📄 Report saved to: {report_path}")
        return str(report_path)
    
    def run_full_validation(self, generation_results: List[Dict[str, Any]], reference_dir: str = None) -> Dict[str, str]:
        """Run complete validation pipeline"""
        print("🚀 Starting full character validation pipeline...")
        
        # Load reference images if provided
        if reference_dir:
            self.load_reference_images(reference_dir)
        
        # Download generated images
        image_paths = self.download_images(generation_results)
        
        # Analyze all images
        analyses = self.analyze_all_images(image_paths, generation_results)
        
        # Calculate metrics
        metrics = self.calculate_consistency_metrics(analyses)
        
        # Generate visualizations
        viz_path = self.generate_visualizations(analyses, metrics)
        
        # Generate report
        report_path = self.generate_report(analyses, metrics)
        
        # Save raw data
        data_path = self.results_dir / f"analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(data_path, 'w') as f:
            # Convert analyses to serializable format
            serializable_analyses = []
            for a in analyses:
                serializable_analyses.append({
                    "image_path": a.image_path,
                    "character": a.character,
                    "location": a.location,
                    "age_group": a.age_group,
                    "confidence_score": a.confidence_score,
                    "face_detected": a.face_detected,
                    "num_faces": len(a.face_encodings)
                })
            
            json.dump({
                "analyses": serializable_analyses,
                "metrics": metrics,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        
        print("✅ Full validation pipeline complete!")
        return {
            "report": report_path,
            "visualization": str(viz_path),
            "data": str(data_path)
        }


def main():
    """Main function for standalone execution"""
    # Example usage
    validator = CharacterValidationSystem()
    
    # This would be called with actual generation results
    print("Character validation system initialized.")
    print("Use validator.run_full_validation(generation_results) to analyze images.")


if __name__ == "__main__":
    main()