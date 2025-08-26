#!/usr/bin/env python3
"""
Generate test photos for character consistency validation
Tests Ferwanda and Ferwando across different ages and locations.
"""

import os
import json
import asyncio
import replicate
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class CharacterConsistencyTester:
    def __init__(self, replicate_token: str):
        os.environ["REPLICATE_API_TOKEN"] = replicate_token
        self.model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        self.lora_strength = 0.8
        self.output_dir = Path("validation/test_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Define test scenarios for character consistency"""
        return [
            # QT Office scenarios
            {
                "location": "QT_office",
                "character": "ferwanda",
                "age": "young_adult",
                "prompt": "ferwanda, young woman, professional business attire, modern office setting, QT company office, glass windows, contemporary interior design, natural lighting, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, multiple people, wrong person"
            },
            {
                "location": "QT_office", 
                "character": "ferwando",
                "age": "young_adult",
                "prompt": "ferwando, young man, professional business attire, modern office setting, QT company office, glass windows, contemporary interior design, natural lighting, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, multiple people, wrong person"
            },
            {
                "location": "QT_office",
                "character": "both",
                "age": "young_adult", 
                "prompt": "ferwanda and ferwando, twin siblings, professional business attire, modern office meeting room, QT company office, collaborative work environment, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, extra people, wrong faces"
            },
            
            # Great Wall scenarios
            {
                "location": "Great_Wall",
                "character": "ferwanda",
                "age": "young_adult",
                "prompt": "ferwanda, young woman, casual tourist outfit, Great Wall of China, ancient stone wall, mountainous landscape, clear blue sky, tourist photo, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, multiple people, wrong person, modern buildings"
            },
            {
                "location": "Great_Wall",
                "character": "ferwando", 
                "age": "young_adult",
                "prompt": "ferwando, young man, casual tourist outfit, Great Wall of China, ancient stone wall, mountainous landscape, clear blue sky, tourist photo, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, multiple people, wrong person, modern buildings"
            },
            {
                "location": "Great_Wall",
                "character": "both",
                "age": "young_adult",
                "prompt": "ferwanda and ferwando, twin siblings, casual tourist clothes, Great Wall of China, ancient stone wall, scenic mountain backdrop, travel photography, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, extra people, wrong faces, modern buildings"
            },
            
            # Indonesian Embassy scenarios
            {
                "location": "Indonesian_Embassy",
                "character": "ferwanda",
                "age": "young_adult", 
                "prompt": "ferwanda, young woman, formal diplomatic attire, Indonesian Embassy building, official government setting, Indonesian flag, formal portrait, professional photography, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, multiple people, wrong person, casual clothes"
            },
            {
                "location": "Indonesian_Embassy",
                "character": "ferwando",
                "age": "young_adult",
                "prompt": "ferwando, young man, formal diplomatic attire, Indonesian Embassy building, official government setting, Indonesian flag, formal portrait, professional photography, polaroid style, vintage aesthetic", 
                "negative_prompt": "blurry, low quality, distorted, multiple people, wrong person, casual clothes"
            },
            {
                "location": "Indonesian_Embassy",
                "character": "both",
                "age": "young_adult",
                "prompt": "ferwanda and ferwando, twin siblings, formal diplomatic attire, Indonesian Embassy reception, official government ceremony, Indonesian cultural elements, formal photography, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, extra people, wrong faces, casual setting"
            },
            
            # Age variation tests
            {
                "location": "QT_office",
                "character": "ferwanda",
                "age": "teenager",
                "prompt": "ferwanda, teenage girl, school uniform or casual young clothes, modern office setting during bring-your-child-to-work day, youthful appearance, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, adult appearance, wrong person"
            },
            {
                "location": "Great_Wall", 
                "character": "ferwando",
                "age": "middle_aged",
                "prompt": "ferwando, middle-aged man, mature appearance, casual travel clothes, Great Wall of China, more mature facial features, family vacation photo, polaroid style, vintage aesthetic",
                "negative_prompt": "blurry, low quality, distorted, young appearance, wrong person"
            }
        ]
    
    async def generate_single_photo(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single test photo"""
        print(f"🎨 Generating: {scenario['character']} at {scenario['location']} ({scenario['age']})")
        
        try:
            output = replicate.run(
                self.model,
                input={
                    "prompt": scenario["prompt"],
                    "negative_prompt": scenario["negative_prompt"],
                    "width": 1024,
                    "height": 1024,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                    "scheduler": "K_EULER",
                    "num_outputs": 1,
                    "high_noise_frac": 0.8,
                    "apply_watermark": False
                }
            )
            
            if output and len(output) > 0:
                image_url = output[0]
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{scenario['character']}_{scenario['location']}_{scenario['age']}_{timestamp}.png"
                
                result = {
                    "scenario": scenario,
                    "image_url": image_url,
                    "filename": filename,
                    "generated_at": datetime.now().isoformat(),
                    "success": True
                }
                
                print(f"✅ Generated: {filename}")
                return result
            else:
                raise Exception("No output from model")
                
        except Exception as e:
            print(f"❌ Failed to generate {scenario['character']} at {scenario['location']}: {e}")
            return {
                "scenario": scenario,
                "error": str(e),
                "success": False,
                "generated_at": datetime.now().isoformat()
            }
    
    async def generate_all_test_photos(self) -> List[Dict[str, Any]]:
        """Generate all test photos"""
        scenarios = self.get_test_scenarios()
        results = []
        
        print(f"🚀 Starting generation of {len(scenarios)} test photos...")
        
        # Generate photos sequentially to avoid rate limits
        for scenario in scenarios:
            result = await self.generate_single_photo(scenario)
            results.append(result)
            
            # Small delay between generations
            await asyncio.sleep(2)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]]):
        """Save generation results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"generation_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Results saved to {results_file}")
        
        # Generate summary
        successful = len([r for r in results if r.get("success", False)])
        failed = len(results) - successful
        
        print(f"\n📈 Generation Summary:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {successful/len(results)*100:.1f}%")
        
        return results_file
    
    def generate_validation_prompts(self) -> List[str]:
        """Generate additional validation prompts for consistency testing"""
        return [
            # Character recognition prompts
            "ferwanda, close-up portrait, detailed facial features, professional headshot",
            "ferwando, close-up portrait, detailed facial features, professional headshot",
            
            # Style consistency prompts
            "ferwanda, polaroid photo, vintage 1980s aesthetic, soft lighting",
            "ferwando, polaroid photo, vintage 1980s aesthetic, soft lighting",
            
            # Expression variety
            "ferwanda, smiling naturally, candid moment, warm expression",
            "ferwando, serious professional expression, confident pose",
            
            # Together prompts
            "ferwanda and ferwando, twin siblings, family portrait, matching outfits",
            "ferwanda and ferwando, laughing together, candid sibling moment"
        ]


async def main():
    """Main function to run character consistency tests"""
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        return
    
    tester = CharacterConsistencyTester(replicate_token)
    
    # Generate test photos
    results = await tester.generate_all_test_photos()
    
    # Save results
    results_file = tester.save_results(results)
    
    print(f"\n🎉 Character consistency test generation complete!")
    print(f"📁 Results saved to: {results_file}")
    print("\nNext steps:")
    print("1. Download generated images")
    print("2. Run face similarity analysis")
    print("3. Generate consistency report")


if __name__ == "__main__":
    asyncio.run(main())