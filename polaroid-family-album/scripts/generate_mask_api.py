#!/usr/bin/env python3
"""
API wrapper for mask generation system
Handles HTTP requests and provides JSON responses.
"""

import os
import sys
import argparse
import json
import requests
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from mask_generation_system import IntegrationMaskGenerator
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Warning: {e}. Some features may not be available.")


def download_image(url: str, output_path: str) -> bool:
    """Download image from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate integration mask via API")
    parser.add_argument("--original-url", required=True, help="Original image URL")
    parser.add_argument("--width", type=int, required=True, help="Friend width")
    parser.add_argument("--height", type=int, required=True, help="Friend height")
    parser.add_argument("--placement", default="right", choices=["left", "right", "center", "background"])
    parser.add_argument("--description", default="", help="Friend description")
    parser.add_argument("--preserve-subjects", action="store_true", help="Preserve existing subjects")
    
    args = parser.parse_args()
    
    try:
        print(f"🎭 Starting mask generation...")
        print(f"   Original URL: {args.original_url[:50]}...")
        print(f"   Friend size: {args.width}x{args.height}")
        print(f"   Placement: {args.placement}")
        
        # Create temporary directory
        temp_dir = Path("temp/mask_generation")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Download original image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_path = temp_dir / f"original_{timestamp}.jpg"
        
        if not download_image(args.original_url, str(original_path)):
            raise Exception("Failed to download original image")
        
        # Load image
        original_image = cv2.imread(str(original_path))
        if original_image is None:
            raise Exception("Failed to load downloaded image")
        
        # Initialize mask generator
        generator = IntegrationMaskGenerator()
        
        # Generate mask
        result = generator.generate_integration_mask(
            original_image,
            (args.width, args.height),
            args.placement,
            args.description,
            args.preserve_subjects
        )
        
        if result.success:
            # Save mask result
            generator.save_mask_result(result, str(temp_dir), f"integration_{timestamp}")
            
            print("✅ Mask generation completed successfully!")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Placement region: {result.placement_region}")
            
            # Output JSON for API consumption
            api_result = {
                "success": True,
                "confidence": result.confidence,
                "placement_region": result.placement_region,
                "composition_analysis": result.composition_analysis,
                "mask_path": f"{temp_dir}/integration_{timestamp}_mask_{timestamp}.png"
            }
            
            print("API_RESULT:", json.dumps(api_result, default=str))
            
        else:
            print(f"❌ Mask generation failed: {result.error_message}")
            api_result = {
                "success": False,
                "error": result.error_message
            }
            print("API_RESULT:", json.dumps(api_result))
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        api_result = {
            "success": False,
            "error": str(e)
        }
        print("API_RESULT:", json.dumps(api_result))
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())