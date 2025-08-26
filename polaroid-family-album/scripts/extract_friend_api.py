#!/usr/bin/env python3
"""
API wrapper for friend extraction processor
Handles HTTP requests and provides JSON responses.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from friend_extraction_processor import FriendExtractionProcessor
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Warning: {e}. Some features may not be available.")


def main():
    parser = argparse.ArgumentParser(description="Extract friend from photo via API")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--description", required=True, help="Friend description")
    parser.add_argument("--method", default="advanced", choices=["basic", "advanced", "ai_segmentation"])
    
    args = parser.parse_args()
    
    try:
        print(f"🔍 Starting friend extraction...")
        print(f"   Input: {args.input}")
        print(f"   Method: {args.method}")
        print(f"   Description: {args.description}")
        
        # Check if input file exists
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Initialize processor
        processor = FriendExtractionProcessor()
        
        # Extract friend
        result = processor.extract_friend_from_photo(
            args.input, 
            args.description,
            args.method
        )
        
        if result.success:
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processor.save_extraction_result(result, args.output, f"friend_{timestamp}")
            
            print("✅ Friend extraction completed successfully!")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Bounding box: {result.bounding_box}")
            
            # Output JSON for API consumption
            api_result = {
                "success": True,
                "confidence": result.confidence,
                "bounding_box": result.bounding_box,
                "lighting_analysis": result.lighting_analysis,
                "extracted_image_path": f"{args.output}/friend_{timestamp}_extracted_{timestamp}.png",
                "mask_path": f"{args.output}/friend_{timestamp}_mask_{timestamp}.png"
            }
            
            print("API_RESULT:", json.dumps(api_result))
            
        else:
            print(f"❌ Friend extraction failed: {result.error_message}")
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