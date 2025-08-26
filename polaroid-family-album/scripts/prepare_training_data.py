#!/usr/bin/env python3
"""
Training Data Preparation Script for Ferwanda & Ferwando LoRA Training
Prepares images and captions for character consistency training.
"""

import os
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps
import argparse


class TrainingDataPreparator:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.min_resolution = 512
        self.max_resolution = 1024
        
    def prepare_datasets(self):
        """Prepare training datasets for both characters"""
        print("🚀 Starting training data preparation...")
        
        # Create output directories
        ferwanda_dir = self.output_dir / "ferwanda"
        ferwando_dir = self.output_dir / "ferwando" 
        combined_dir = self.output_dir / "combined"
        
        for dir_path in [ferwanda_dir, ferwando_dir, combined_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Process individual character images
        self.process_character_images("ferwanda", ferwanda_dir)
        self.process_character_images("ferwando", ferwando_dir)
        
        # Create combined dataset for dual character training
        self.create_combined_dataset(combined_dir)
        
        # Generate training config
        self.generate_training_config()
        
        print("✅ Training data preparation complete!")
        
    def process_character_images(self, character_name: str, output_dir: Path):
        """Process images for a specific character"""
        print(f"📸 Processing images for {character_name}...")
        
        character_input_dir = self.input_dir / character_name
        if not character_input_dir.exists():
            print(f"⚠️  Warning: No input directory found for {character_name}")
            return
        
        processed_count = 0
        for img_file in character_input_dir.glob("*.{jpg,jpeg,png,webp}"):
            try:
                # Process image
                processed_img = self.process_image(img_file)
                if processed_img:
                    # Save processed image
                    output_filename = f"{character_name}_{processed_count:03d}.jpg"
                    output_path = output_dir / output_filename
                    processed_img.save(output_path, "JPEG", quality=95)
                    
                    # Generate caption
                    caption = self.generate_caption(character_name, processed_count)
                    caption_path = output_dir / f"{character_name}_{processed_count:03d}.txt"
                    with open(caption_path, 'w') as f:
                        f.write(caption)
                    
                    processed_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing {img_file}: {e}")
        
        print(f"✅ Processed {processed_count} images for {character_name}")
        
    def process_image(self, image_path: Path) -> Image.Image:
        """Process individual image for training"""
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF
            img = ImageOps.exif_transpose(img)
            
            # Resize while maintaining aspect ratio
            img = self.resize_image(img)
            
            return img
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None
    
    def resize_image(self, img: Image.Image) -> Image.Image:
        """Resize image for training while maintaining aspect ratio"""
        width, height = img.size
        
        # Calculate new size
        if width > height:
            if width > self.max_resolution:
                height = int(height * self.max_resolution / width)
                width = self.max_resolution
        else:
            if height > self.max_resolution:
                width = int(width * self.max_resolution / height) 
                height = self.max_resolution
        
        # Ensure minimum resolution
        if width < self.min_resolution or height < self.min_resolution:
            scale = max(self.min_resolution / width, self.min_resolution / height)
            width = int(width * scale)
            height = int(height * scale)
        
        # Make dimensions divisible by 64 (required for SDXL)
        width = (width // 64) * 64
        height = (height // 64) * 64
        
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    def generate_caption(self, character_name: str, image_index: int) -> str:
        """Generate training caption for character"""
        base_captions = {
            "ferwanda": [
                "ferwanda, a young woman with distinctive facial features",
                "ferwanda, professional portrait, clear facial details",
                "ferwanda, natural lighting, high quality photo",
                "ferwanda, smiling, looking at camera",
                "ferwanda, casual portrait, detailed face"
            ],
            "ferwando": [
                "ferwando, a young man with distinctive facial features", 
                "ferwando, professional portrait, clear facial details",
                "ferwando, natural lighting, high quality photo",
                "ferwando, smiling, looking at camera",
                "ferwando, casual portrait, detailed face"
            ]
        }
        
        caption_variations = base_captions.get(character_name, [f"{character_name}, portrait"])
        return caption_variations[image_index % len(caption_variations)]
    
    def create_combined_dataset(self, output_dir: Path):
        """Create combined dataset for both characters together"""
        print("👫 Creating combined dataset...")
        
        combined_captions = [
            "ferwanda and ferwando, twin siblings, professional portrait",
            "ferwanda and ferwando, two people, family photo", 
            "ferwanda and ferwando, brother and sister, smiling",
            "ferwanda and ferwando, twins, looking at camera",
            "ferwanda and ferwando, portrait of two siblings"
        ]
        
        # This would typically combine individual photos or create composite images
        # For now, create placeholder captions for manual photo selection
        for i, caption in enumerate(combined_captions):
            caption_path = output_dir / f"combined_{i:03d}.txt"
            with open(caption_path, 'w') as f:
                f.write(caption)
        
        print("📝 Combined dataset templates created")
    
    def generate_training_config(self):
        """Generate training configuration files"""
        config = {
            "model_name": "ferwanda_ferwando_lora_v1",
            "base_model": "stabilityai/stable-diffusion-xl-base-1.0",
            "resolution": "1024x1024",
            "train_batch_size": 1,
            "learning_rate": 1e-4,
            "max_train_steps": 1000,
            "network_dim": 64,
            "network_alpha": 32,
            "lr_scheduler": "cosine",
            "optimizer_type": "AdamW8bit",
            "mixed_precision": "fp16",
            "save_precision": "fp16",
            "sample_every_n_steps": 100,
            "sample_prompts": [
                "ferwanda, professional portrait, polaroid style",
                "ferwando, professional portrait, polaroid style", 
                "ferwanda and ferwando, family photo, polaroid style"
            ]
        }
        
        config_path = self.output_dir / "training_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️  Training config saved to {config_path}")


def main():
    parser = argparse.ArgumentParser(description="Prepare training data for LoRA training")
    parser.add_argument("--input", default="raw_photos", help="Input directory with raw photos")
    parser.add_argument("--output", default="training_data", help="Output directory for processed data")
    
    args = parser.parse_args()
    
    preparator = TrainingDataPreparator(args.input, args.output)
    preparator.prepare_datasets()


if __name__ == "__main__":
    main()