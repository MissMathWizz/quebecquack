# Add Friend to Family Photo

Add a friend to existing family photo: $ARGUMENTS

## Steps:
1. Process uploaded friend photo for face extraction
2. Generate integration mask for optimal placement
3. Use stable-diffusion-inpainting model
4. Maintain Polaroid aesthetic consistency
5. Create new album entry with friend integration

## Implementation:
- Use MediaPipe for face detection and extraction from friend photo
- Generate placement mask using semantic segmentation
- Apply SDXL inpainting model with friend features
- Preserve original photo's Polaroid aesthetic (lighting, color tone, grain)
- Save composite image to `public/generated/with_friends/`
- Update album metadata with friend information and integration details