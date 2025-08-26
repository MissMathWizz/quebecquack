#!/usr/bin/env python3
"""
Simple demo of the character consistency validation system
Shows the pipeline without requiring CV dependencies.
"""

import json
import random
from datetime import datetime
from pathlib import Path


def create_demo_validation_report():
    """Create a demo validation report"""
    print("🚀 Creating Demo Character Consistency Report")
    print("="*50)
    
    # Mock scenarios
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
    
    # Generate mock confidence scores
    results = []
    for scenario in scenarios:
        # Base confidence
        confidence = 0.75
        
        # Character adjustments
        if scenario["character"] == "ferwanda":
            confidence += 0.08
        elif scenario["character"] == "ferwando":
            confidence += 0.05
        else:  # both
            confidence -= 0.15
        
        # Location adjustments
        if scenario["location"] == "QT_office":
            confidence += 0.10
        elif scenario["location"] == "Great_Wall":
            confidence += 0.05
        else:  # Indonesian_Embassy
            confidence -= 0.08
        
        # Age adjustments
        if scenario["age"] == "teenager":
            confidence -= 0.25
        elif scenario["age"] == "middle_aged":
            confidence -= 0.12
        
        # Add randomness
        confidence += random.uniform(-0.08, 0.08)
        confidence = max(0.1, min(0.98, confidence))
        
        results.append({
            "scenario": scenario,
            "confidence_score": confidence,
            "face_detected": confidence > 0.3
        })
    
    # Calculate metrics
    total_images = len(results)
    faces_detected = len([r for r in results if r["face_detected"]])
    confidences = [r["confidence_score"] for r in results if r["face_detected"]]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    high_conf = len([c for c in confidences if c > 0.8])
    low_conf = len([c for c in confidences if c < 0.4])
    
    # Create validation directory
    validation_dir = Path("validation/analysis_results")
    validation_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = validation_dir / f"demo_consistency_report_{timestamp}.md"
    
    with open(report_path, 'w') as f:
        f.write("# Ferwanda & Ferwando Character Consistency Validation Demo\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("**Type:** Demo simulation with mock data\n\n")
        
        # Executive Summary
        f.write("## 📊 Executive Summary\n\n")
        f.write(f"- **Total Images Analyzed:** {total_images}\n")
        f.write(f"- **Face Detection Rate:** {faces_detected/total_images:.1%}\n")
        f.write(f"- **Average Confidence Score:** {avg_confidence:.3f}\n")
        f.write(f"- **High Confidence Images:** {high_conf} (>0.8)\n")
        f.write(f"- **Low Confidence Images:** {low_conf} (<0.4)\n\n")
        
        # Character Performance
        f.write("## 👥 Character-Specific Results\n\n")
        
        for character in ["ferwanda", "ferwando", "both"]:
            char_results = [r for r in results if r["scenario"]["character"] == character]
            char_confidences = [r["confidence_score"] for r in char_results if r["face_detected"]]
            
            if char_confidences:
                f.write(f"### {character.title()}\n")
                f.write(f"- **Images:** {len(char_results)}\n")
                f.write(f"- **Detection Rate:** {len([r for r in char_results if r['face_detected']])}/{len(char_results)} ({len([r for r in char_results if r['face_detected']])/len(char_results):.1%})\n")
                f.write(f"- **Average Confidence:** {sum(char_confidences)/len(char_confidences):.3f}\n")
                f.write(f"- **Best Score:** {max(char_confidences):.3f}\n")
                f.write(f"- **Worst Score:** {min(char_confidences):.3f}\n\n")
        
        # Location Performance
        f.write("## 📍 Location-Specific Results\n\n")
        
        for location in ["QT_office", "Great_Wall", "Indonesian_Embassy"]:
            loc_results = [r for r in results if r["scenario"]["location"] == location]
            loc_confidences = [r["confidence_score"] for r in loc_results if r["face_detected"]]
            
            location_name = location.replace("_", " ").title()
            f.write(f"### {location_name}\n")
            
            if loc_confidences:
                f.write(f"- **Images:** {len(loc_results)}\n")
                f.write(f"- **Detection Rate:** {len([r for r in loc_results if r['face_detected']])}/{len(loc_results)} ({len([r for r in loc_results if r['face_detected']])/len(loc_results):.1%})\n")
                f.write(f"- **Average Confidence:** {sum(loc_confidences)/len(loc_confidences):.3f}\n")
                
                # Performance insights
                avg_score = sum(loc_confidences)/len(loc_confidences)
                if avg_score > 0.8:
                    f.write("- **Performance:** ✅ Excellent\n")
                elif avg_score > 0.7:
                    f.write("- **Performance:** ✅ Good\n")
                elif avg_score > 0.6:
                    f.write("- **Performance:** ⚠️ Moderate\n")
                else:
                    f.write("- **Performance:** ❌ Needs Improvement\n")
                f.write("\n")
        
        # Age Variation Analysis
        f.write("## 🎭 Age Variation Results\n\n")
        
        age_groups = set(r["scenario"]["age"] for r in results)
        for age in age_groups:
            age_results = [r for r in results if r["scenario"]["age"] == age]
            age_confidences = [r["confidence_score"] for r in age_results if r["face_detected"]]
            
            age_name = age.replace("_", " ").title()
            f.write(f"### {age_name}\n")
            
            if age_confidences:
                avg_score = sum(age_confidences)/len(age_confidences)
                f.write(f"- **Images:** {len(age_results)}\n")
                f.write(f"- **Average Confidence:** {avg_score:.3f}\n")
                
                if age == "young_adult":
                    f.write("- **Analysis:** Baseline age group with optimal performance\n")
                elif age == "teenager":
                    f.write("- **Analysis:** Challenging due to facial development differences\n")
                elif age == "middle_aged":
                    f.write("- **Analysis:** Moderate challenge due to aging features\n")
                f.write("\n")
        
        # Detailed Results Table
        f.write("## 📋 Detailed Results\n\n")
        f.write("| Character | Location | Age | Confidence | Status |\n")
        f.write("|-----------|----------|-----|------------|--------|\n")
        
        for result in results:
            scenario = result["scenario"]
            conf = result["confidence_score"]
            status = "✅ Pass" if conf > 0.6 else "⚠️ Review" if conf > 0.4 else "❌ Fail"
            
            f.write(f"| {scenario['character']} | {scenario['location'].replace('_', ' ')} | {scenario['age'].replace('_', ' ')} | {conf:.3f} | {status} |\n")
        
        # Insights and Recommendations
        f.write("\n## 🔍 Key Insights\n\n")
        
        # Find best and worst performers
        best_result = max(results, key=lambda x: x["confidence_score"])
        worst_result = min(results, key=lambda x: x["confidence_score"])
        
        f.write(f"- **Best Performance:** {best_result['scenario']['character']} at {best_result['scenario']['location']} ({best_result['confidence_score']:.3f})\n")
        f.write(f"- **Needs Improvement:** {worst_result['scenario']['character']} at {worst_result['scenario']['location']} ({worst_result['confidence_score']:.3f})\n")
        
        # Character insights
        ferwanda_scores = [r["confidence_score"] for r in results if r["scenario"]["character"] == "ferwanda" and r["face_detected"]]
        ferwando_scores = [r["confidence_score"] for r in results if r["scenario"]["character"] == "ferwando" and r["face_detected"]]
        
        if ferwanda_scores and ferwando_scores:
            ferwanda_avg = sum(ferwanda_scores) / len(ferwanda_scores)
            ferwando_avg = sum(ferwando_scores) / len(ferwando_scores)
            
            if ferwanda_avg > ferwando_avg:
                f.write(f"- **Character Consistency:** Ferwanda shows higher consistency ({ferwanda_avg:.3f} vs {ferwando_avg:.3f})\n")
            else:
                f.write(f"- **Character Consistency:** Ferwando shows higher consistency ({ferwando_avg:.3f} vs {ferwanda_avg:.3f})\n")
        
        f.write("\n## 🚀 Next Steps\n\n")
        f.write("1. **LoRA Training:** Use `scripts/prepare_training_data.py` to prepare training images\n")
        f.write("2. **GPU Setup:** Run `scripts/setup_runpod_training.py` to configure training environment\n")
        f.write("3. **Real Testing:** Execute `scripts/run_consistency_test.py` with actual API tokens\n")
        f.write("4. **Model Refinement:** Adjust training parameters based on validation results\n")
        f.write("5. **Production Integration:** Deploy validated models to the family album app\n")
        
        f.write("\n---\n")
        f.write("*This demo report simulates the validation pipeline. For actual results, train LoRA models with real photos and run consistency tests with the Replicate API.*\n")
    
    # Print summary
    print(f"📄 Demo report generated: {report_path}")
    print(f"\n📊 Demo Results Summary:")
    print(f"   Total Images: {total_images}")
    print(f"   Detection Rate: {faces_detected/total_images:.1%}")
    print(f"   Average Confidence: {avg_confidence:.3f}")
    print(f"   High Confidence: {high_conf}")
    print(f"   Low Confidence: {low_conf}")
    
    print(f"\n🎯 Character Performance:")
    for character in ["ferwanda", "ferwando", "both"]:
        char_results = [r for r in results if r["scenario"]["character"] == character]
        char_confidences = [r["confidence_score"] for r in char_results if r["face_detected"]]
        if char_confidences:
            avg = sum(char_confidences) / len(char_confidences)
            print(f"   {character.title()}: {avg:.3f}")
    
    print(f"\n📍 Location Performance:")
    for location in ["QT_office", "Great_Wall", "Indonesian_Embassy"]:
        loc_results = [r for r in results if r["scenario"]["location"] == location]
        loc_confidences = [r["confidence_score"] for r in loc_results if r["face_detected"]]
        if loc_confidences:
            avg = sum(loc_confidences) / len(loc_confidences)
            location_name = location.replace("_", " ")
            print(f"   {location_name}: {avg:.3f}")
    
    return report_path


if __name__ == "__main__":
    create_demo_validation_report()
    print("\n✅ Demo complete! Check the generated report for detailed results.")
    print("\n🔧 To run with real data:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Set REPLICATE_API_TOKEN environment variable")  
    print("   3. Run: python scripts/run_consistency_test.py")
    print("   4. Or use the web UI at http://localhost:3000/validation")