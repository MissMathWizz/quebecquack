# Train LoRA for Character Consistency

Setup LoRA training for character consistency: $ARGUMENTS

## Steps:
1. Prepare training dataset from provided character images
2. Configure RunPod GPU instance for training
3. Use SDXL base model with rank 64, alpha 32
4. Train for 1000 steps with 1e-4 learning rate
5. Test character consistency across scenarios

## Implementation:
- Organize training images in `./training_data/characters/` with proper captions
- Set up Kohya Scripts environment on RunPod GPU instance
- Configure training parameters:
  - Network rank: 64
  - Network alpha: 32
  - Learning rate: 1e-4
  - Batch size: 1
  - Mixed precision: fp16
- Run training for 1000 steps with sample generation every 100 steps
- Save final LoRA weights to `./models/` directory
- Generate test images to verify character consistency