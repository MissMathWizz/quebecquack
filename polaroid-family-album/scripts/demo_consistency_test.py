#!/usr/bin/env python3
"""
Demo script to test the character consistency validation system
Creates mock results to demonstrate the validation pipeline.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from character_validation_system import CharacterValidationSystem


def create_mock_generation_results():
    """Create mock generation results for testing"""
    mock_results = []
    
    scenarios = [
        {"character": "ferwanda", "location": "QT_office", "age": "young_adult"},
        {"character": "ferwando", "location": "QT_office", "age": "young_adult"},
        {"character": "both", "location": "QT_office", "age": "young_adult"},
        {"character": "ferwanda", "location": "Great_Wall", "age": "young_adult"},
        {"character": "ferwando", "location": "Great_Wall", "age": "young_adult"},
        {"character": "both", "location": "Great_Wall", "age": "young_adult"},
        {"character": "ferwanda", "location": "Indonesian_Embassy", "age": "young_adult"},
        {"character": "ferwando", "location": "Indonesian_Embassy", "age": "young_adult"},
        {"character": "both", "location": "Indonesian_Embassy", "age": "young_adult"},
        {"character": "ferwanda", "location": "QT_office", "age": "teenager"},
        {"character": "ferwando", "location": "Great_Wall", "age": "middle_aged"}
    ]
    
    for i, scenario in enumerate(scenarios):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario['character']}_{scenario['location']}_{scenario['age']}_{timestamp}_{i:02d}.png"
        
        # Use placeholder images for demo
        mock_result = {
            "scenario": {
                "location": scenario["location"],
                "character": scenario["character"],
                "age": scenario["age"],
                "prompt": f"{scenario['character']} at {scenario['location']}, {scenario['age']}, polaroid style",
                "negative_prompt": "blurry, low quality, distorted"
            },
            "image_url": f"https://picsum.photos/1024/1024?random={i}",  # Placeholder images
            "filename": filename,
            "generated_at": datetime.now().isoformat(),
            "success": True
        }
        
        mock_results.append(mock_result)
    
    return mock_results


def run_demo_validation():
    """Run the demo validation test"""
    print("🚀 Starting Demo Character Consistency Validation")
    print("="*60)
    
    # Create mock results
    print("📝 Creating mock generation results...")
    mock_results = create_mock_generation_results()
    
    # Save mock results
    validation_dir = Path("validation")
    validation_dir.mkdir(exist_ok=True)
    
    results_file = validation_dir / f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(mock_results, f, indent=2)
    
    print(f"💾 Mock results saved to: {results_file}")
    
    # Initialize validation system
    print("🔧 Initializing validation system...")
    validator = CharacterValidationSystem()
    
    # Since we're using placeholder images, we'll create a mock analysis
    print("📊 Running mock validation analysis...")
    
    # Create mock analyses (normally this would analyze actual faces)
    mock_analyses = []
    for result in mock_results:
        scenario = result["scenario"]
        
        # Mock confidence scores based on character and location
        base_confidence = 0.7
        
        # Simulate different confidence levels
        if scenario["character"] == "ferwanda":
            confidence = base_confidence + 0.1
        elif scenario["character"] == "ferwando":
            confidence = base_confidence + 0.05
        else:  # both
            confidence = base_confidence - 0.1
        
        # Location variations
        if scenario["location"] == "QT_office":
            confidence += 0.1
        elif scenario["location"] == "Great_Wall":
            confidence += 0.05
        else:  # Indonesian_Embassy
            confidence -= 0.05
        
        # Age variations
        if scenario["age"] == "teenager":
            confidence -= 0.2
        elif scenario["age"] == "middle_aged":
            confidence -= 0.1
        
        # Add some randomness
        import random
        confidence += random.uniform(-0.1, 0.1)
        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        
        mock_analysis = {
            "image_path": f"validation/test_images/{result['filename']}",
            "character": scenario["character"],
            "location": scenario["location"],
            "age_group": scenario["age"],
            "confidence_score": confidence,
            "face_detected": True,
            "num_faces": 2 if scenario["character"] == "both" else 1
        }
        
        mock_analyses.append(mock_analysis)
    
    # Calculate metrics using mock data
    print("📈 Calculating consistency metrics...")
    
    total_images = len(mock_analyses)
    faces_detected = len([a for a in mock_analyses if a["face_detected"]])
    confidences = [a["confidence_score"] for a in mock_analyses if a["face_detected"]]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    high_conf = len([c for c in confidences if c > 0.8])
    low_conf = len([c for c in confidences if c < 0.4])
    
    metrics = {
        "overall_stats": {
            "total_images": total_images,
            "faces_detected": faces_detected,
            "detection_rate": faces_detected / total_images,
            "average_confidence": avg_confidence,
            "high_confidence_count": high_conf,
            "low_confidence_count": low_conf
        },
        "character_stats": {},
        "location_stats": {},
        "age_stats": {}
    }
    
    # Character-specific stats
    for character in ["ferwanda", "ferwando", "both"]:
        char_analyses = [a for a in mock_analyses if a["character"] == character]
        if char_analyses:
            char_confidences = [a["confidence_score"] for a in char_analyses if a["face_detected"]]
            metrics["character_stats"][character] = {
                "total_images": len(char_analyses),
                "faces_detected": len([a for a in char_analyses if a["face_detected"]]),
                "average_confidence": sum(char_confidences) / len(char_confidences) if char_confidences else 0,
                "std_confidence": 0.1,  # Mock value
                "min_confidence": min(char_confidences) if char_confidences else 0,
                "max_confidence": max(char_confidences) if char_confidences else 0
            }
    
    # Location stats
    for location in ["QT_office", "Great_Wall", "Indonesian_Embassy"]:
        loc_analyses = [a for a in mock_analyses if a["location"] == location]
        if loc_analyses:
            loc_confidences = [a["confidence_score"] for a in loc_analyses if a["face_detected"]]
            metrics["location_stats"][location] = {
                "total_images": len(loc_analyses),
                "faces_detected": len([a for a in loc_analyses if a["face_detected"]]),
                "average_confidence": sum(loc_confidences) / len(loc_confidences) if loc_confidences else 0
            }
    
    # Age stats  
    for age in ["young_adult", "teenager", "middle_aged"]:
        age_analyses = [a for a in mock_analyses if a["age_group"] == age]
        if age_analyses:
            age_confidences = [a["confidence_score"] for a in age_analyses if a["face_detected"]]
            metrics["age_stats"][age] = {
                "total_images": len(age_analyses),
                "faces_detected": len([a for a in age_analyses if a["face_detected"]]),
                "average_confidence": sum(age_confidences) / len(age_confidences) if age_confidences else 0
            }
    
    # Generate demo report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = validation_dir / f"demo_report_{timestamp}.md"
    
    with open(report_path, 'w') as f:
        f.write("# Demo Character Consistency Validation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("**Note:** This is a demonstration using mock data and placeholder images.\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        overall = metrics['overall_stats']
        f.write(f"- **Total Images Analyzed:** {overall['total_images']}\n")
        f.write(f"- **Face Detection Rate:** {overall['detection_rate']:.1%}\n") 
        f.write(f"- **Average Confidence Score:** {overall['average_confidence']:.3f}\n")
        f.write(f"- **High Confidence Images:** {overall['high_confidence_count']} (>0.8)\n")
        f.write(f"- **Low Confidence Images:** {overall['low_confidence_count']} (<0.4)\n\n")
        
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
        
        f.write("## Demo Results Summary\n\n")
        f.write("This demo shows how the validation system would work with real generated images:\n\n")
        f.write("1. **QT Office** scenarios show highest confidence (professional lighting)\n")
        f.write("2. **Great Wall** scenarios show good performance (outdoor natural light)\n")
        f.write("3. **Indonesian Embassy** scenarios show moderate performance (formal setting challenges)\n")
        f.write("4. **Age variations** show expected confidence drops for non-standard ages\n")
        f.write("5. **Dual character** images show lower confidence due to complexity\n\n")
        f.write("**Next Steps:**\n")
        f.write("- Train LoRA models with actual Ferwanda & Ferwando photos\n")
        f.write("- Run real generation tests with REPLICATE_API_TOKEN\n")
        f.write("- Analyze actual face consistency with reference images\n")
    
    print(f"📄 Demo report generated: {report_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DEMO RESULTS SUMMARY")
    print("="*60)
    print(f"Total Images: {overall['total_images']}")
    print(f"Detection Rate: {overall['detection_rate']:.1%}")
    print(f"Average Confidence: {overall['average_confidence']:.3f}")
    print(f"High Confidence (>0.8): {overall['high_confidence_count']}")
    print(f"Low Confidence (<0.4): {overall['low_confidence_count']}")
    
    print("\nCharacter Performance:")
    for char, stats in metrics['character_stats'].items():
        print(f"  {char}: {stats['average_confidence']:.3f}")
    
    print("\nLocation Performance:")
    for loc, stats in metrics['location_stats'].items():
        print(f"  {loc}: {stats['average_confidence']:.3f}")
    
    print(f"\n📁 Files generated:")
    print(f"  📝 Results: {results_file}")
    print(f"  📄 Report: {report_path}")
    
    print("\n🎉 Demo validation complete!")
    print("\nTo run with real images:")
    print("1. Set REPLICATE_API_TOKEN environment variable")
    print("2. Run: python scripts/run_consistency_test.py")
    print("3. Or use the web interface at /validation")


if __name__ == "__main__":
    run_demo_validation()