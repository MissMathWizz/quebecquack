# Polaroid Family Album 📸

An interactive family album application that combines traditional photo storage with AI-powered photo generation capabilities using custom LoRA models.

## Features

- **Interactive Polaroid-Style Interface**: Flip photos to see metadata and generation details
- **AI Photo Generation**: Generate new family photos using custom-trained LoRA models
- **Real-time Camera Capture**: Take photos directly in the app
- **File Upload Support**: Upload existing photos from your device
- **Social Interactions**: Like, comment, and share family photos
- **Invitation System**: Share albums with family and friends using invitation codes
- **Custom LoRA Training**: Train models on your family photos for consistent character generation

## Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, Supabase
- **Database**: PostgreSQL (via Supabase)
- **AI Generation**: Replicate API with SDXL + custom LoRA models
- **Authentication**: Supabase Auth
- **File Storage**: Supabase Storage / AWS S3

## Quick Start

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd polaroid-family-album
   npm install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env.local
   # Fill in your API keys and configuration
   ```

3. **Database Setup**
   ```bash
   # Create a new Supabase project
   # Run the SQL schema in supabase/schema.sql
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   ```

5. **Open** [http://localhost:3000](http://localhost:3000)

## Environment Variables

Copy `.env.example` to `.env.local` and configure:

- `REPLICATE_API_TOKEN`: Your Replicate API token for AI generation
- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

## Project Structure

```
src/
├── app/                 # Next.js 13+ app directory
│   ├── api/            # API routes
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
│   ├── PolaroidPhoto.tsx    # Interactive Polaroid component
│   ├── AlbumPage.tsx        # Main album interface
│   └── CameraInterface.tsx  # Photo capture/AI generation
├── lib/                # Utilities and services
│   ├── supabase.ts     # Database operations
│   └── replicate.ts    # AI generation service
└── types/              # TypeScript definitions
```

## Custom Commands

Use the following Claude Code commands:

- `/generate-family` - Generate family photos with LoRA models
- `/add-friend` - Add friends to existing photos using inpainting
- `/train-lora` - Set up LoRA training for character consistency

## AI Generation

The app uses Replicate's SDXL model with custom LoRA weights trained on family photos:

- **Base Model**: Stability AI SDXL
- **LoRA Strength**: 0.8 (configurable)
- **Style**: Automatic Polaroid aesthetic enhancement
- **Resolution**: 1024x1024

## Database Schema

Key tables:
- `profiles`: User information
- `albums`: Photo collections
- `photos`: Individual photos with metadata
- `user_interactions`: Likes, comments, shares
- `lora_models`: Custom trained models
- `invitation_codes`: Album sharing system

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Self-hosting

1. Build the application: `npm run build`
2. Start production server: `npm start`
3. Configure reverse proxy (nginx/caddy)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the GitHub Issues page
- Review the documentation in `/docs`
- Join our community discussions