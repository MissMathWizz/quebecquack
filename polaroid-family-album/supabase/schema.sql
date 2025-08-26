-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable Row Level Security
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Create custom types
CREATE TYPE interaction_type AS ENUM ('like', 'comment', 'share');

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Albums table
CREATE TABLE public.albums (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    invitation_code TEXT UNIQUE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Photos table
CREATE TABLE public.photos (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    url TEXT NOT NULL,
    caption TEXT,
    album_id UUID REFERENCES public.albums(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    is_generated BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User interactions table (likes, comments, shares)
CREATE TABLE public.user_interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    photo_id UUID REFERENCES public.photos(id) ON DELETE CASCADE NOT NULL,
    interaction_type interaction_type NOT NULL,
    content TEXT, -- For comments
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Album collaborators (for shared albums)
CREATE TABLE public.album_collaborators (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    album_id UUID REFERENCES public.albums(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    role TEXT DEFAULT 'viewer' CHECK (role IN ('owner', 'editor', 'viewer')),
    invited_by UUID REFERENCES public.profiles(id),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(album_id, user_id)
);

-- LoRA models table (for storing custom trained models)
CREATE TABLE public.lora_models (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    model_url TEXT NOT NULL,
    training_images_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invitation codes table
CREATE TABLE public.invitation_codes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    album_id UUID REFERENCES public.albums(id) ON DELETE CASCADE NOT NULL,
    created_by UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    max_uses INTEGER DEFAULT 1,
    current_uses INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_photos_album_id ON public.photos(album_id);
CREATE INDEX idx_photos_user_id ON public.photos(user_id);
CREATE INDEX idx_photos_created_at ON public.photos(created_at DESC);
CREATE INDEX idx_user_interactions_photo_id ON public.user_interactions(photo_id);
CREATE INDEX idx_user_interactions_user_id ON public.user_interactions(user_id);
CREATE INDEX idx_album_collaborators_album_id ON public.album_collaborators(album_id);
CREATE INDEX idx_album_collaborators_user_id ON public.album_collaborators(user_id);
CREATE INDEX idx_invitation_codes_code ON public.invitation_codes(code);
CREATE INDEX idx_invitation_codes_album_id ON public.invitation_codes(album_id);

-- Row Level Security Policies

-- Profiles RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Albums RLS
ALTER TABLE public.albums ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own albums" ON public.albums
    FOR SELECT USING (
        auth.uid() = user_id OR 
        is_public = TRUE OR
        auth.uid() IN (
            SELECT user_id FROM public.album_collaborators 
            WHERE album_id = albums.id
        )
    );

CREATE POLICY "Users can create albums" ON public.albums
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own albums" ON public.albums
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own albums" ON public.albums
    FOR DELETE USING (auth.uid() = user_id);

-- Photos RLS
ALTER TABLE public.photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view photos in accessible albums" ON public.photos
    FOR SELECT USING (
        auth.uid() = user_id OR
        album_id IN (
            SELECT id FROM public.albums 
            WHERE is_public = TRUE OR 
                  user_id = auth.uid() OR
                  id IN (
                      SELECT album_id FROM public.album_collaborators 
                      WHERE user_id = auth.uid()
                  )
        )
    );

CREATE POLICY "Users can insert photos in accessible albums" ON public.photos
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND
        album_id IN (
            SELECT id FROM public.albums 
            WHERE user_id = auth.uid() OR
                  id IN (
                      SELECT album_id FROM public.album_collaborators 
                      WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
                  )
        )
    );

CREATE POLICY "Users can update their own photos" ON public.photos
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own photos" ON public.photos
    FOR DELETE USING (auth.uid() = user_id);

-- User interactions RLS
ALTER TABLE public.user_interactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view interactions on accessible photos" ON public.user_interactions
    FOR SELECT USING (
        photo_id IN (
            SELECT id FROM public.photos 
            WHERE album_id IN (
                SELECT id FROM public.albums 
                WHERE is_public = TRUE OR 
                      user_id = auth.uid() OR
                      id IN (
                          SELECT album_id FROM public.album_collaborators 
                          WHERE user_id = auth.uid()
                      )
            )
        )
    );

CREATE POLICY "Users can create their own interactions" ON public.user_interactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own interactions" ON public.user_interactions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own interactions" ON public.user_interactions
    FOR DELETE USING (auth.uid() = user_id);

-- Album collaborators RLS
ALTER TABLE public.album_collaborators ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view collaborators of accessible albums" ON public.album_collaborators
    FOR SELECT USING (
        auth.uid() = user_id OR
        album_id IN (
            SELECT id FROM public.albums 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Album owners can manage collaborators" ON public.album_collaborators
    FOR ALL USING (
        album_id IN (
            SELECT id FROM public.albums 
            WHERE user_id = auth.uid()
        )
    );

-- LoRA models RLS
ALTER TABLE public.lora_models ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own LoRA models" ON public.lora_models
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own LoRA models" ON public.lora_models
    FOR ALL USING (auth.uid() = user_id);

-- Invitation codes RLS
ALTER TABLE public.invitation_codes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view invitation codes for their albums" ON public.invitation_codes
    FOR SELECT USING (
        created_by = auth.uid() OR
        album_id IN (
            SELECT id FROM public.albums 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create invitation codes for their albums" ON public.invitation_codes
    FOR INSERT WITH CHECK (
        created_by = auth.uid() AND
        album_id IN (
            SELECT id FROM public.albums 
            WHERE user_id = auth.uid()
        )
    );

-- Functions for common operations

-- Function to generate unique invitation codes
CREATE OR REPLACE FUNCTION generate_invitation_code()
RETURNS TEXT AS $$
BEGIN
    RETURN upper(substring(md5(random()::text) from 1 for 8));
END;
$$ LANGUAGE plpgsql;

-- Function to handle profile creation on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to update updated_at timestamps
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_albums_updated_at
    BEFORE UPDATE ON public.albums
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_photos_updated_at
    BEFORE UPDATE ON public.photos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lora_models_updated_at
    BEFORE UPDATE ON public.lora_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();