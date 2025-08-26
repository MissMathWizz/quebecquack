# Generate Family Photo

Generate a family photo using our custom LoRA models for Ferwanda and Ferwando at: $ARGUMENTS

## Steps:
1. Use Replicate API with SDXL base model
2. Apply Ferwanda-Ferwando LoRA at 0.8 strength  
3. Include Polaroid aesthetic prompts
4. Save to public/generated/ with timestamp
5. Update album metadata

## Implementation:
- Load custom LoRA weights from `./models/ferwanda-ferwando.safetensors`
- Apply Polaroid-style prompts: "vintage polaroid photo, soft lighting, slightly faded colors"
- Generate 1024x1024 resolution with 30 inference steps
- Save with filename format: `family_YYYYMMDD_HHMMSS.png`
- Update `album_metadata.json` with new entry