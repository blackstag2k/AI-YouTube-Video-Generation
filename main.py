# main.py - ALL-IN-ONE YOUTUBE VIDEO GENERATION PIPELINE
"""
Complete AI-powered YouTube video generation pipeline.
All modules combined into a single file for easy deployment.

Author: [Bhaskar Rana]
Created: 2026
License: MIT
"""

import google.genai as genai
import asyncio
import edge_tts
import requests
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    concatenate_videoclips
)

# ============================================================================
# CONFIGURATION - ADD YOUR API KEYS HERE
# ============================================================================

GEMINI_API_KEY = "ENTER_GEMINI_API_KEY"
PEXELS_API_KEY = "ENTER_PEXELS_API_KEY"

# ============================================================================
# GLOBAL SETTINGS
# ============================================================================

OUTPUT_DIR = Path("output")
ASSETS_DIR = OUTPUT_DIR / "assets"

MAX_RETRIES = 3
RETRY_DELAY = 2

# Video settings
DEFAULT_DURATION = 60
VIDEO_RESOLUTION = (1920, 1080)
FPS = 30
NUM_VIDEOS = 3

# Voice options
VOICES = {
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-JennyNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_au": "en-AU-WilliamNeural",
    "female_au": "en-AU-NatashaNeural"
}
DEFAULT_VOICE = "female_us"

# Pexels API endpoints
PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"
PEXELS_PHOTO_API = "https://api.pexels.com/v1/search"

# Thumbnail settings
THUMBNAIL_SIZE = (1280, 720)

# ============================================================================
# MODULE 1: SCRIPT GENERATION
# ============================================================================

def generate_script(topic, duration_seconds=60):
    """
    Generate a YouTube video script using Gemini.
    
    Args:
        topic: The video topic
        duration_seconds: Target video length (default 60s)
    
    Returns:
        str: The generated script or None if failed
    """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    words_per_second = 2.5
    target_words = int(duration_seconds * words_per_second)
    
    prompt = f"""You are a professional YouTube script writer.

TOPIC: {topic}
DURATION: {duration_seconds} seconds
TARGET WORDS: {target_words} words

Create a YouTube video script with:
- Strong hook in the first 5 seconds to grab attention
- 3 clear main points with explanations
- Conversational, energetic tone
- Call to action at the end
- Approximately {target_words} words (for {duration_seconds} seconds at natural speaking pace)

Rules:
- NO markdown formatting
- NO stage directions or scene descriptions
- ONLY the narration text that will be spoken
- Natural conversational flow
- Engaging and easy to understand

Write the script now:"""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            script = response.text.strip()
            script = script.replace("**", "").replace("*", "")
            
            return script
        
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Script generation attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def save_script_output(topic, script, duration_seconds):
    """Save script and metadata to JSON file"""
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    word_count = len(script.split())
    char_count = len(script)
    estimated_duration = word_count / 2.5
    
    output_data = {
        "topic": topic,
        "target_duration": duration_seconds,
        "script": script,
        "stats": {
            "word_count": word_count,
            "character_count": char_count,
            "estimated_duration_seconds": round(estimated_duration, 1)
        }
    }
    
    output_file = OUTPUT_DIR / "script.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    
    script_file = OUTPUT_DIR / "script.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"✅ Script saved to: {output_file}")
    
    return output_data


# ============================================================================
# MODULE 2: VOICE GENERATION
# ============================================================================

async def generate_voice_async(text, voice_name, output_path):
    """
    Generate voice audio from text using Edge TTS.
    
    Args:
        text: The script text to convert to speech
        voice_name: Voice identifier from VOICES dict
        output_path: Path to save the audio file
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    voice = VOICES.get(voice_name, VOICES[DEFAULT_VOICE])
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))
            return True
        
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Voice generation attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return False


def generate_voice(text, voice_name=DEFAULT_VOICE, output_filename="voiceover.mp3"):
    """
    Synchronous wrapper for voice generation.
    
    Args:
        text: The script text
        voice_name: Voice type (default: female_us)
        output_filename: Name of output file
    
    Returns:
        Path: Path to generated audio file or None if failed
    """
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    
    success = asyncio.run(generate_voice_async(text, voice_name, output_path))
    
    if not success:
        return None
    
    return output_path


def save_voice_metadata(script, voice_name, audio_path, duration_seconds):
    """Save voice generation metadata to JSON"""
    
    metadata = {
        "script": script,
        "voice": voice_name,
        "voice_full_name": VOICES.get(voice_name, VOICES[DEFAULT_VOICE]),
        "audio_file": str(audio_path),
        "estimated_duration_seconds": duration_seconds
    }
    
    output_file = OUTPUT_DIR / "voice_metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Voice metadata saved to: {output_file}")
    
    return metadata


# ============================================================================
# MODULE 3: VISUAL FETCHING
# ============================================================================

def search_videos(query, per_page=5, orientation="landscape"):
    """
    Search for videos on Pexels.
    
    Args:
        query: Search query
        per_page: Number of results to fetch
        orientation: Video orientation
    
    Returns:
        list: List of video data or None if failed
    """
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                PEXELS_VIDEO_API,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("videos", [])
            elif response.status_code == 401:
                print("❌ Invalid Pexels API key")
                return None
            
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Video search attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def get_best_video_file(video_files, target_width=1920):
    """Select the best video file from available options"""
    
    sorted_files = sorted(
        video_files,
        key=lambda x: abs(x.get("width", 0) - target_width)
    )
    
    return sorted_files[0] if sorted_files else None


def download_video(url, filename):
    """Download video from URL"""
    
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = ASSETS_DIR / filename
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return output_path
            
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Download attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def fetch_visuals(topic, num_videos=3):
    """
    Fetch and download videos related to the topic.
    
    Args:
        topic: Search topic/keywords
        num_videos: Number of videos to download
    
    Returns:
        list: List of downloaded video paths
    """
    
    print(f"🔍 Searching Pexels for: '{topic}'")
    
    videos = search_videos(topic, per_page=num_videos)
    
    if not videos:
        raise RuntimeError(f"No videos found for topic: {topic}")
    
    print(f"✅ Found {len(videos)} videos")
    
    downloaded_videos = []
    
    for idx, video in enumerate(videos[:num_videos], 1):
        video_id = video.get("id")
        video_files = video.get("video_files", [])
        
        if not video_files:
            print(f"⚠️ No files available for video {idx}")
            continue
        
        best_file = get_best_video_file(video_files)
        
        if not best_file:
            print(f"⚠️ Could not determine best file for video {idx}")
            continue
        
        download_url = best_file.get("link")
        filename = f"video_{idx}.mp4"
        
        print(f"⬇️ Downloading video {idx}/{num_videos}...")
        
        video_path = download_video(download_url, filename)
        
        if video_path:
            downloaded_videos.append({
                "path": str(video_path),
                "id": video_id,
                "width": best_file.get("width"),
                "height": best_file.get("height"),
                "duration": video.get("duration"),
                "url": video.get("url")
            })
            print(f"✅ Downloaded: {video_path}")
        else:
            print(f"❌ Failed to download video {idx}")
    
    if not downloaded_videos:
        raise RuntimeError("Failed to download any videos")
    
    return downloaded_videos


def save_visuals_metadata(topic, videos):
    """Save visual assets metadata to JSON"""
    
    metadata = {
        "topic": topic,
        "total_videos": len(videos),
        "videos": videos
    }
    
    output_file = OUTPUT_DIR / "visuals_metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Visuals metadata saved to: {output_file}")
    
    return metadata


# ============================================================================
# MODULE 4: VIDEO CREATION
# ============================================================================

def load_metadata():
    """Load all metadata from previous pipeline steps"""
    
    script_file = OUTPUT_DIR / "script.json"
    voice_file = OUTPUT_DIR / "voice_metadata.json"
    visuals_file = OUTPUT_DIR / "visuals_metadata.json"
    
    if not script_file.exists():
        raise FileNotFoundError("script.json not found")
    if not voice_file.exists():
        raise FileNotFoundError("voice_metadata.json not found")
    if not visuals_file.exists():
        raise FileNotFoundError("visuals_metadata.json not found")
    
    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)
    with open(voice_file, "r", encoding="utf-8") as f:
        voice_data = json.load(f)
    with open(visuals_file, "r", encoding="utf-8") as f:
        visuals_data = json.load(f)
    
    return script_data, voice_data, visuals_data


def resize_and_crop(clip, target_size):
    """Resize and crop video to target resolution"""
    
    target_width, target_height = target_size
    target_ratio = target_width / target_height
    
    clip_width, clip_height = clip.size
    clip_ratio = clip_width / clip_height
    
    if clip_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * clip_ratio)
        resized = clip.resize(height=new_height)
        x_center = resized.w / 2
        x1 = x_center - target_width / 2
        cropped = resized.crop(x1=x1, width=target_width)
    else:
        new_width = target_width
        new_height = int(new_width / clip_ratio)
        resized = clip.resize(width=new_width)
        y_center = resized.h / 2
        y1 = y_center - target_height / 2
        cropped = resized.crop(y1=y1, height=target_height)
    
    return cropped


def create_video(audio_path, video_paths, output_filename="final_video.mp4"):
    """
    Create final video by combining audio and visuals.
    
    Args:
        audio_path: Path to audio file
        video_paths: List of video file paths
        output_filename: Output video filename
    
    Returns:
        Path: Path to created video or None if failed
    """
    
    print("🎬 Loading audio...")
    audio = AudioFileClip(str(audio_path))
    audio_duration = audio.duration
    
    print(f"   Audio duration: {audio_duration:.2f}s")
    
    print(f"🎥 Loading {len(video_paths)} video clips...")
    video_clips = []
    
    for idx, video_path in enumerate(video_paths, 1):
        try:
            clip = VideoFileClip(str(video_path))
            processed_clip = resize_and_crop(clip, VIDEO_RESOLUTION)
            processed_clip = processed_clip.set_fps(FPS)
            processed_clip = processed_clip.without_audio()
            video_clips.append(processed_clip)
            print(f"   ✅ Loaded video {idx}: {Path(video_path).name}")
        except Exception as e:
            print(f"   ⚠️ Failed to load video {idx}: {e}")
    
    if not video_clips:
        raise RuntimeError("No valid video clips loaded")
    
    duration_per_clip = audio_duration / len(video_clips)
    print(f"\n⏱️ Duration per clip: {duration_per_clip:.2f}s")
    
    adjusted_clips = []
    
    for idx, clip in enumerate(video_clips, 1):
        if clip.duration >= duration_per_clip:
            trimmed = clip.subclip(0, duration_per_clip)
            adjusted_clips.append(trimmed)
        else:
            loops_needed = int(duration_per_clip / clip.duration) + 1
            looped = concatenate_videoclips([clip] * loops_needed)
            trimmed = looped.subclip(0, duration_per_clip)
            adjusted_clips.append(trimmed)
        
        print(f"   Clip {idx}: {clip.duration:.2f}s → {duration_per_clip:.2f}s")
    
    print("\n🔗 Concatenating video clips...")
    final_video = concatenate_videoclips(adjusted_clips, method="compose")
    
    print("🎵 Adding audio track...")
    final_video = final_video.set_audio(audio)
    
    output_path = OUTPUT_DIR / output_filename
    
    print(f"\n💾 Exporting final video to: {output_path}")
    print("   This may take a few minutes...\n")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=FPS,
                preset='medium',
                threads=4
            )
            
            audio.close()
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Video export attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def save_video_metadata(output_path, audio_duration, num_clips):
    """Save final video metadata to JSON"""
    
    metadata = {
        "output_file": str(output_path),
        "resolution": f"{VIDEO_RESOLUTION[0]}x{VIDEO_RESOLUTION[1]}",
        "fps": FPS,
        "duration_seconds": audio_duration,
        "num_video_clips": num_clips
    }
    
    output_file = OUTPUT_DIR / "video_metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Video metadata saved to: {output_file}")
    
    return metadata


# ============================================================================
# MODULE 5: THUMBNAIL GENERATION
# ============================================================================

def generate_thumbnail_text(topic, script):
    """Generate catchy thumbnail text using Gemini"""
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""You are a YouTube thumbnail expert.

TOPIC: {topic}
SCRIPT PREVIEW: {script[:500]}...

Create catchy thumbnail text that will get clicks:

Requirements:
- Main text: 3-5 words MAX, eye-catching, curiosity-provoking
- Subtitle (optional): 2-4 words supporting text
- Use power words (Amazing, Secret, Shocking, Ultimate, etc.)
- Make it emotionally compelling
- Related to the video content

Return ONLY a JSON object:
{{
    "main_text": "your main text here",
    "subtitle": "optional subtitle or empty string"
}}

No other text, just the JSON."""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            return data
        
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Thumbnail text generation attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def search_thumbnail_image(query):
    """Search for a background image on Pexels"""
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": 5,
        "orientation": "landscape"
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                PEXELS_PHOTO_API,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                if photos:
                    return photos[0]["src"]["large2x"]
            
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Image search attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def download_image(url):
    """Download image from URL"""
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"Image download attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def create_thumbnail(background_image, main_text, subtitle=""):
    """Create thumbnail with text overlay"""
    
    bg = background_image.resize(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    overlay = Image.new('RGBA', THUMBNAIL_SIZE, (0, 0, 0, 120))
    bg = bg.convert('RGBA')
    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)
    
    try:
        font_paths = [
            "C:/Windows/Fonts/impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Impact.ttf"
        ]
        
        main_font = None
        for font_path in font_paths:
            if Path(font_path).exists():
                main_font = ImageFont.truetype(font_path, 100)
                break
        
        if main_font is None:
            main_font = ImageFont.load_default()
    except:
        main_font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), main_text, font=main_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (THUMBNAIL_SIZE[0] - text_width) // 2
    y = (THUMBNAIL_SIZE[1] - text_height) // 2
    
    outline_color = (0, 0, 0)
    text_color = (255, 255, 255)
    
    for offset_x in [-3, 0, 3]:
        for offset_y in [-3, 0, 3]:
            draw.text((x + offset_x, y + offset_y), main_text, font=main_font, fill=outline_color)
    
    draw.text((x, y), main_text, font=main_font, fill=text_color)
    
    if subtitle:
        try:
            subtitle_font = ImageFont.truetype(font_paths[0], 40) if Path(font_paths[0]).exists() else ImageFont.load_default()
        except:
            subtitle_font = ImageFont.load_default()
        
        bbox_sub = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox_sub[2] - bbox_sub[0]
        
        sub_x = (THUMBNAIL_SIZE[0] - sub_width) // 2
        sub_y = y + text_height + 20
        
        for offset_x in [-2, 0, 2]:
            for offset_y in [-2, 0, 2]:
                draw.text((sub_x + offset_x, sub_y + offset_y), subtitle, font=subtitle_font, fill=outline_color)
        
        draw.text((sub_x, sub_y), subtitle, font=subtitle_font, fill=(255, 255, 0))
    
    return bg.convert('RGB')


def generate_thumbnail(topic, script, output_filename="thumbnail.jpg"):
    """Generate complete thumbnail"""
    
    print("💭 Generating thumbnail text...")
    text_data = generate_thumbnail_text(topic, script)
    
    if not text_data:
        raise RuntimeError("Failed to generate thumbnail text")
    
    main_text = text_data["main_text"]
    subtitle = text_data.get("subtitle", "")
    
    print(f"   Main text: {main_text}")
    if subtitle:
        print(f"   Subtitle: {subtitle}")
    
    print(f"\n🔍 Searching for background image: '{topic}'")
    image_url = search_thumbnail_image(topic)
    
    if not image_url:
        raise RuntimeError("Failed to find background image")
    
    print(f"   Found image")
    
    print("\n⬇️ Downloading image...")
    background = download_image(image_url)
    
    if not background:
        raise RuntimeError("Failed to download image")
    
    print("✅ Image downloaded")
    
    print("\n🎨 Creating thumbnail...")
    thumbnail = create_thumbnail(background, main_text, subtitle)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    thumbnail.save(output_path, quality=95)
    
    return output_path


# ============================================================================
# MODULE 6: SEO METADATA GENERATION
# ============================================================================

def generate_seo_metadata(topic, script):
    """Generate YouTube SEO metadata using Gemini"""
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""You are a YouTube SEO expert.

TOPIC: {topic}
SCRIPT: {script}

Create optimized YouTube metadata:

Requirements for TITLE:
- 60 characters or less
- Include main keyword
- Compelling and click-worthy
- Clear and descriptive

Requirements for DESCRIPTION:
- 150-200 words
- First 2-3 sentences should hook viewers
- Include relevant keywords naturally
- Add timestamps if applicable
- Include call-to-action
- Mention what viewers will learn

Requirements for TAGS:
- 10-15 relevant tags
- Mix of broad and specific keywords
- Include variations of main topic
- Use multi-word phrases

Return ONLY a JSON object:
{{
    "title": "your optimized title",
    "description": "your full description",
    "tags": ["tag1", "tag2", "tag3", ...]
}}

No other text, just the JSON."""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            return data
        
        except Exception as e:
            time.sleep(RETRY_DELAY)
            print(f"SEO generation attempt {attempt}/{MAX_RETRIES} failed. Error: {e}")
    
    return None


def save_seo_metadata(seo_data):
    """Save SEO metadata to JSON"""
    
    output_file = OUTPUT_DIR / "seo_metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(seo_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ SEO metadata saved to: {output_file}")
    
    return output_file


# ============================================================================
# MODULE 7: SUBTITLE GENERATION
# ============================================================================

def format_time_srt(seconds):
    """Format time for SRT subtitle format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_subtitles_from_script(script):
    """Generate simple subtitles from script"""
    
    sentences = [s.strip() + '.' for s in script.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    words_per_second = 2.5
    subtitles = []
    current_time = 0
    
    for sentence in sentences:
        word_count = len(sentence.split())
        duration = word_count / words_per_second
        
        subtitles.append({
            "start": round(current_time, 2),
            "end": round(current_time + duration, 2),
            "text": sentence
        })
        
        current_time += duration
    
    return subtitles


def create_srt_file(subtitles, output_filename="subtitles.srt"):
    """Create SRT subtitle file"""
    
    output_path = OUTPUT_DIR / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, sub in enumerate(subtitles, 1):
            f.write(f"{idx}\n")
            f.write(f"{format_time_srt(sub['start'])} --> {format_time_srt(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")
    
    return output_path


def generate_subtitles(use_speech_recognition=False):
    """Generate subtitles for the video"""
    
    script_file = OUTPUT_DIR / "script.json"
    
    if not script_file.exists():
        raise FileNotFoundError("script.json not found")
    
    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)
    
    script = script_data["script"]
    
    print("📄 Generating subtitles from script...")
    subtitles = generate_subtitles_from_script(script)
    
    print("\n💾 Creating SRT file...")
    srt_path = create_srt_file(subtitles)
    
    return srt_path


def save_subtitles_metadata(srt_path, num_segments):
    """Save subtitles metadata"""
    
    metadata = {
        "subtitle_file": str(srt_path),
        "format": "SRT",
        "num_segments": num_segments
    }
    
    output_file = OUTPUT_DIR / "subtitles_metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Subtitles metadata saved to: {output_file}")
    
    return metadata


# ============================================================================
# MODULE 8: YOUTUBE UPLOAD PREPARATION
# ============================================================================

def prepare_youtube_upload():
    """Prepare all metadata for YouTube upload"""
    
    seo_file = OUTPUT_DIR / "seo_metadata.json"
    video_file = OUTPUT_DIR / "final_video.mp4"
    thumbnail_file = OUTPUT_DIR / "thumbnail.jpg"
    subtitles_file = OUTPUT_DIR / "subtitles.srt"
    
    if not seo_file.exists():
        raise FileNotFoundError("seo_metadata.json not found")
    
    if not video_file.exists():
        raise FileNotFoundError("final_video.mp4 not found")
    
    with open(seo_file, "r", encoding="utf-8") as f:
        seo_data = json.load(f)
    
    upload_data = {
        "video_file": str(video_file),
        "title": seo_data["title"],
        "description": seo_data["description"],
        "tags": seo_data["tags"],
        "category": "22",
        "privacy": "public",
        "thumbnail_file": str(thumbnail_file) if thumbnail_file.exists() else None,
        "subtitles_file": str(subtitles_file) if subtitles_file.exists() else None
    }
    
    return upload_data


def save_upload_instructions(upload_data):
    """Save upload instructions and metadata"""
    
    output_file = OUTPUT_DIR / "youtube_upload_guide.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(upload_data, f, ensure_ascii=False, indent=4)
    
    guide_file = OUTPUT_DIR / "YOUTUBE_UPLOAD_INSTRUCTIONS.txt"
    
    with open(guide_file, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("YOUTUBE UPLOAD INSTRUCTIONS\n")
        f.write("="*70 + "\n\n")
        
        f.write("📹 VIDEO FILE:\n")
        f.write(f"   {upload_data['video_file']}\n\n")
        
        f.write(f"📌 TITLE ({len(upload_data['title'])} characters):\n")
        f.write(f"   {upload_data['title']}\n\n")
        
        f.write("📝 DESCRIPTION:\n")
        f.write(f"   {upload_data['description']}\n\n")
        
        f.write("🏷️ TAGS (copy and paste these):\n")
        f.write("   " + ", ".join(upload_data['tags']) + "\n\n")
        
        if upload_data['thumbnail_file']:
            f.write("🖼️ THUMBNAIL:\n")
            f.write(f"   {upload_data['thumbnail_file']}\n\n")
        
        if upload_data['subtitles_file']:
            f.write("💬 SUBTITLES:\n")
            f.write(f"   {upload_data['subtitles_file']}\n\n")
        
        f.write("="*70 + "\n")
        f.write("MANUAL UPLOAD STEPS:\n")
        f.write("="*70 + "\n\n")
        f.write("1. Go to https://studio.youtube.com\n")
        f.write("2. Click 'CREATE' → 'Upload videos'\n")
        f.write("3. Select the video file listed above\n")
        f.write("4. Copy-paste the title from above\n")
        f.write("5. Copy-paste the description from above\n")
        f.write("6. Add the tags listed above\n")
        f.write("7. Upload the thumbnail file\n")
        f.write("8. Upload subtitles (if available)\n")
        f.write("9. Set visibility to 'Public' (or your preference)\n")
        f.write("10. Click 'PUBLISH'\n\n")
    
    print(f"✅ Upload guide saved to: {guide_file}")


# ============================================================================
# MASTER PIPELINE ORCHESTRATION
# ============================================================================

def print_section_header(step_num, total_steps, title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"STEP {step_num}/{total_steps}: {title}")
    print("="*70 + "\n")


def run_complete_pipeline(topic, duration_seconds=60, voice_name=DEFAULT_VOICE, 
                          num_videos=3, generate_bonuses=True):
    """
    Run the complete end-to-end YouTube video generation pipeline.
    
    Args:
        topic: Video topic
        duration_seconds: Target video duration
        voice_name: Voice type for TTS
        num_videos: Number of background videos to fetch
        generate_bonuses: Generate thumbnail, SEO, subtitles
    
    Returns:
        dict: Complete pipeline output data
    """
    
    total_steps = 8 if generate_bonuses else 4
    
    print("\n" + "="*70)
    print("🎬 MASTER YOUTUBE VIDEO GENERATION PIPELINE")
    print("="*70)
    print(f"Topic: {topic}")
    print(f"Duration: {duration_seconds}s")
    print(f"Voice: {voice_name}")
    print(f"Videos: {num_videos}")
    print(f"Bonuses: {'Yes' if generate_bonuses else 'No'}")
    print("="*70)
    
    pipeline_start_time = datetime.now()
    results = {}
    
    try:
        # ====================================================================
        # STEP 1: Generate Script
        # ====================================================================
        print_section_header(1, total_steps, "Generating Script")
        
        script = generate_script(topic, duration_seconds)
        
        if not script:
            raise RuntimeError("❌ Script generation failed")
        
        print(f"✅ Script generated ({len(script.split())} words)")
        
        script_data = save_script_output(topic, script, duration_seconds)
        results['script'] = script_data
        
        # ====================================================================
        # STEP 2: Generate Voiceover
        # ====================================================================
        print_section_header(2, total_steps, "Generating Voiceover")
        
        audio_path = generate_voice(script, voice_name)
        
        if not audio_path:
            raise RuntimeError("❌ Voice generation failed")
        
        print(f"✅ Voiceover generated: {audio_path}")
        
        word_count = len(script.split())
        estimated_duration = word_count / 2.5
        
        voice_metadata = save_voice_metadata(script, voice_name, audio_path, estimated_duration)
        results['voice'] = voice_metadata
        
        # ====================================================================
        # STEP 3: Fetch Visuals
        # ====================================================================
        print_section_header(3, total_steps, "Fetching Visual Assets")
        
        videos = fetch_visuals(topic, num_videos=num_videos)
        
        if not videos:
            raise RuntimeError("❌ Visual fetching failed")
        
        print(f"✅ Downloaded {len(videos)} videos")
        
        visuals_metadata = save_visuals_metadata(topic, videos)
        results['visuals'] = visuals_metadata
        
        # ====================================================================
        # STEP 4: Create Video
        # ====================================================================
        print_section_header(4, total_steps, "Creating Final Video")
        
        script_data_reload, voice_data_reload, visuals_data_reload = load_metadata()
        
        audio_path_reload = Path(voice_data_reload["audio_file"])
        video_paths = [Path(v["path"]) for v in visuals_data_reload["videos"]]
        
        video_path = create_video(audio_path_reload, video_paths)
        
        if not video_path:
            raise RuntimeError("❌ Video creation failed")
        
        print(f"✅ Video created: {video_path}")
        
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"📊 File size: {file_size_mb:.2f} MB")
        
        video_metadata = save_video_metadata(video_path, estimated_duration, len(videos))
        results['video'] = video_metadata
        
        # ====================================================================
        # BONUS FEATURES
        # ====================================================================
        if generate_bonuses:
            
            # ================================================================
            # STEP 5: Generate Thumbnail
            # ================================================================
            print_section_header(5, total_steps, "Generating Thumbnail")
            
            try:
                thumbnail_path = generate_thumbnail(topic, script)
                print(f"✅ Thumbnail created: {thumbnail_path}")
                results['thumbnail'] = str(thumbnail_path)
            except Exception as e:
                print(f"⚠️ Thumbnail generation failed: {e}")
                print("Continuing without thumbnail...")
                results['thumbnail'] = None
            
            # ================================================================
            # STEP 6: Generate SEO Metadata
            # ================================================================
            print_section_header(6, total_steps, "Generating SEO Metadata")
            
            try:
                seo_data = generate_seo_metadata(topic, script)
                
                if seo_data:
                    print(f"✅ SEO metadata generated")
                    print(f"   Title: {seo_data['title']}")
                    print(f"   Tags: {len(seo_data['tags'])} tags")
                    
                    save_seo_metadata(seo_data)
                    results['seo'] = seo_data
                else:
                    print("⚠️ SEO generation failed")
                    results['seo'] = None
            except Exception as e:
                print(f"⚠️ SEO generation failed: {e}")
                print("Continuing without SEO...")
                results['seo'] = None
            
            # ================================================================
            # STEP 7: Generate Subtitles
            # ================================================================
            print_section_header(7, total_steps, "Generating Subtitles")
            
            try:
                srt_path = generate_subtitles(use_speech_recognition=False)
                
                with open(srt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    num_segments = content.count('\n\n')
                
                print(f"✅ Subtitles created: {srt_path}")
                print(f"   Segments: {num_segments}")
                
                save_subtitles_metadata(srt_path, num_segments)
                results['subtitles'] = str(srt_path)
            except Exception as e:
                print(f"⚠️ Subtitle generation failed: {e}")
                print("Continuing without subtitles...")
                results['subtitles'] = None
            
            # ================================================================
            # STEP 8: Prepare YouTube Upload
            # ================================================================
            print_section_header(8, total_steps, "Preparing YouTube Upload")
            
            try:
                upload_data = prepare_youtube_upload()
                save_upload_instructions(upload_data)
                
                print("✅ Upload instructions created")
                results['upload_ready'] = True
            except Exception as e:
                print(f"⚠️ Upload preparation failed: {e}")
                results['upload_ready'] = False
        
        # ====================================================================
        # PIPELINE COMPLETE
        # ====================================================================
        pipeline_end_time = datetime.now()
        total_time = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE!")
        print("="*70)
        
        print(f"\n⏱️ Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        
        print("\n📁 Generated Files:")
        print(f"   ✅ Script: output/script.json")
        print(f"   ✅ Voiceover: output/voiceover.mp3")
        print(f"   ✅ Videos: output/assets/ ({len(videos)} files)")
        print(f"   ✅ Final Video: {video_path}")
        
        if generate_bonuses:
            if results.get('thumbnail'):
                print(f"   ✅ Thumbnail: {results['thumbnail']}")
            if results.get('seo'):
                print(f"   ✅ SEO Metadata: output/seo_metadata.json")
            if results.get('subtitles'):
                print(f"   ✅ Subtitles: {results['subtitles']}")
            if results.get('upload_ready'):
                print(f"   ✅ Upload Guide: output/YOUTUBE_UPLOAD_INSTRUCTIONS.txt")
        
        print("\n🎉 Your YouTube video is ready!")
        
        if generate_bonuses and results.get('upload_ready'):
            print("\n📤 Next Steps:")
            print("   1. Review the video: output/final_video.mp4")
            print("   2. Check upload instructions: output/YOUTUBE_UPLOAD_INSTRUCTIONS.txt")
            print("   3. Upload to YouTube!")
        
        return results
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ PIPELINE FAILED")
        print("="*70)
        print(f"\nError: {e}")
        print("\n⚠️ Check the error message above and try again.")
        raise


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 WELCOME TO AI VIDEO GENERATION PIPELINE")
    print("="*70)
    
    # Get user input
    print("\n📌 Enter video details:\n")
    
    topic = input("Video topic: ").strip()
    
    if not topic:
        topic = "The science behind morning coffee"
        print(f"Using default topic: {topic}")
    
    duration_input = input("\nVideo duration in seconds (default=60): ").strip()
    duration = int(duration_input) if duration_input else 60
    
    bonuses_input = input("\nGenerate bonuses (thumbnail, SEO, subtitles)? (Y/n): ").strip().lower()
    generate_bonuses = bonuses_input != 'n'
    
    print("\n" + "="*70)
    print("🎬 Starting pipeline...")
    print("="*70)
    
    try:
        result = run_complete_pipeline(
            topic=topic,
            duration_seconds=duration,
            voice_name=DEFAULT_VOICE,
            num_videos=NUM_VIDEOS,
            generate_bonuses=generate_bonuses
        )
        
        print("\n✅ SUCCESS! Pipeline completed successfully.")
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        sys.exit(1)