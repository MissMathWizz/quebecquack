#!/usr/bin/env python3
"""
Main script to run the complete character consistency test pipeline.
Combines generation and validation for comprehensive testing.
"""

import os
import json
import asyncio
from pathlib import Path
from generate_test_photos import CharacterConsistencyTester
from character_validation_system import CharacterValidationSystem


class ConsistencyTestPipeline:
    def __init__(self, replicate_token: str, reference_images_dir: str = None):
        self.tester = CharacterConsistencyTester(replicate_token)
        self.validator = CharacterValidationSystem()
        self.reference_dir = reference_images_dir
        
    async def run_complete_test(self, generate_new: bool = True, results_file: str = None) -> Dict[str, Any]:
        """Run the complete consistency test pipeline"""
        print("🚀 Starting complete character consistency test pipeline...")
        
        if generate_new:
            print("\n" + "="*50)
            print("PHASE 1: GENERATING TEST PHOTOS")
            print("="*50)
            
            # Generate test photos
            generation_results = await self.tester.generate_all_test_photos()
            
            # Save generation results
            results_file = self.tester.save_results(generation_results)
            
        else:
            # Load existing results
            if not results_file:
                print("❌ No results file provided for validation-only mode")
                return None
                
            with open(results_file, 'r') as f:
                generation_results = json.load(f)
            print(f"📁 Loaded existing results from {results_file}")
        
        print("\n" + "="*50)
        print("PHASE 2: VALIDATING CHARACTER CONSISTENCY")
        print("="*50)
        
        # Run validation
        validation_results = self.validator.run_full_validation(
            generation_results, 
            self.reference_dir
        )
        
        print("\n" + "="*50)
        print("PHASE 3: PIPELINE COMPLETE")
        print("="*50)
        
        # Combine results
        pipeline_results = {
            "generation_file": str(results_file) if results_file else None,
            "validation_results": validation_results,
            "total_images_generated": len([r for r in generation_results if r.get("success", False)]),
            "pipeline_completed": True
        }
        
        # Print summary
        print(f"📊 Pipeline Summary:")
        print(f"   • Images Generated: {pipeline_results['total_images_generated']}")
        print(f"   • Validation Report: {validation_results['report']}")
        print(f"   • Visualization: {validation_results['visualization']}")
        print(f"   • Raw Data: {validation_results['data']}")
        
        return pipeline_results


def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run character consistency test pipeline")
    parser.add_argument("--replicate-token", help="Replicate API token")
    parser.add_argument("--reference-dir", help="Directory with reference images")
    parser.add_argument("--generate", action="store_true", default=True, 
                       help="Generate new test photos (default: True)")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only run validation on existing results")
    parser.add_argument("--results-file", help="Existing results file for validation-only mode")
    
    args = parser.parse_args()
    
    # Get API token
    replicate_token = args.replicate_token or os.getenv("REPLICATE_API_TOKEN")
    if not replicate_token:
        print("❌ Replicate API token required. Set REPLICATE_API_TOKEN or use --replicate-token")
        return
    
    # Initialize pipeline
    pipeline = ConsistencyTestPipeline(replicate_token, args.reference_dir)
    
    # Run pipeline
    try:
        if args.validate_only:
            if not args.results_file:
                print("❌ --results-file required for validation-only mode")
                return
            results = asyncio.run(pipeline.run_complete_test(
                generate_new=False, 
                results_file=args.results_file
            ))
        else:
            results = asyncio.run(pipeline.run_complete_test(generate_new=True))
        
        if results:
            print("\n🎉 Character consistency test pipeline completed successfully!")
            print("\nFiles generated:")
            if results.get("generation_file"):
                print(f"📸 Generation Results: {results['generation_file']}")
            print(f"📄 Validation Report: {results['validation_results']['report']}")
            print(f"📊 Visualization: {results['validation_results']['visualization']}")
            print(f"💾 Raw Data: {results['validation_results']['data']}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()