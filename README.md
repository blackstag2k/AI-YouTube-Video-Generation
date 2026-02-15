# 🎬 AI YouTube Video Generation Pipeline

**Fully automated AI-powered YouTube video generation from a single topic input.**

Generate complete, YouTube-ready videos with script, voiceover, visuals, thumbnail, SEO metadata, and subtitles - all automatically using free AI tools.

---

## 🌟 Features

- ✅ **AI Script Generation** - Gemini 2.0 Flash generates engaging video scripts
- ✅ **Text-to-Speech** - Edge TTS creates natural voiceovers (6 voice options)
- ✅ **Auto Visual Fetching** - Pexels API downloads relevant stock footage
- ✅ **Video Assembly** - MoviePy combines audio + visuals into final MP4
- ✅ **AI Thumbnail** - Auto-generates eye-catching YouTube thumbnails
- ✅ **SEO Optimization** - AI-generated titles, descriptions, and tags
- ✅ **Subtitle Generation** - Creates SRT subtitle files
- ✅ **YouTube Upload Prep** - Complete upload instructions and metadata

---

## 🎥 Demo

**Input:** `"The science behind morning coffee"`

**Output:**
- 60-second YouTube video (1920x1080, 30fps)
- Professional voiceover
- 3 relevant stock video clips
- Custom thumbnail with catchy text
- SEO-optimized metadata
- Subtitle file (.srt)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11.9
- [Gemini API key](https://aistudio.google.com/app/apikey) (free)
- [Pexels API key](https://www.pexels.com/api/) (free)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-video-generator.git
cd ai-video-generator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Open `main.py` and add your API keys:
```python
# Line ~30-35
GEMINI_API_KEY = "your_gemini_api_key_here"
PEXELS_API_KEY = "your_pexels_api_key_here"
```

### Usage
```bash
python main.py
```

Follow the prompts:
1. Enter your video topic
2. Set duration (default: 60 seconds)
3. Choose whether to generate bonuses (thumbnail, SEO, subtitles)

Wait 3-5 minutes, and your complete video package will be in the `output/` folder!

---

## 📁 Project Structure
```
ai-video-generator/
├── main.py                          # ⭐ All-in-one pipeline script
├── requirements.txt                 # Python dependencies
├── PROMPTS.md                       # All AI prompts used
├── README.md                        # This file
├── .gitignore                       # Git ignore rules
└── output/                          # Generated files (created on first run)
    ├── script.json                  # Generated script
    ├── script.txt                   # Plain text script
    ├── voiceover.mp3                # AI voiceover
    ├── final_video.mp4              # ⭐ Final video (main deliverable)
    ├── thumbnail.jpg                # YouTube thumbnail
    ├── subtitles.srt                # Subtitle file
    ├── seo_metadata.json            # SEO data (title, description, tags)
    ├── voice_metadata.json          # Voice generation metadata
    ├── visuals_metadata.json        # Downloaded videos metadata
    ├── video_metadata.json          # Final video metadata
    ├── youtube_upload_guide.json    # Upload data
    ├── YOUTUBE_UPLOAD_INSTRUCTIONS.txt  # Step-by-step upload guide
    └── assets/
        ├── video_1.mp4              # Stock footage clip 1
        ├── video_2.mp4              # Stock footage clip 2
        └── video_3.mp4              # Stock footage clip 3
```

---

## 🛠️ Technology Stack

| Component | Tool | Why |
|-----------|------|-----|
| Script Generation | Google Gemini 2.5 Flash | Fast, free, high-quality content |
| Text-to-Speech | Edge TTS | Free, natural voices, no API key |
| Stock Videos | Pexels API | Free high-quality footage |
| Video Assembly | MoviePy | Python video editing library |
| Thumbnail Creation | PIL + Pexels | Dynamic text overlay on images |
| SEO Optimization | Google Gemini | AI-generated metadata |

---

## 🎯 Use Cases

- **Content Creators** - Rapid video prototyping
- **Educators** - Quick explainer videos
- **Marketers** - Social media content at scale
- **Developers** - Learning AI automation
- **Students** - Assignment automation (like this project!)

---

## 📊 Pipeline Stages
```
Input Topic
    ↓
1. Generate Script (Gemini) → script.json
    ↓
2. Generate Voiceover (Edge TTS) → voiceover.mp3
    ↓
3. Fetch Visuals (Pexels) → video_1.mp4, video_2.mp4, video_3.mp4
    ↓
4. Create Video (MoviePy) → final_video.mp4
    ↓
5. Generate Thumbnail (AI + Pexels) → thumbnail.jpg
    ↓
6. Generate SEO (Gemini) → seo_metadata.json
    ↓
7. Generate Subtitles → subtitles.srt
    ↓
8. Prepare Upload Instructions → YOUTUBE_UPLOAD_INSTRUCTIONS.txt
    ↓
Output: Complete YouTube Video Package
```

---

## ⚙️ Configuration Options

### Voice Options (Line ~45 in main.py)
```python
VOICES = {
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-JennyNeural",      # Default
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_au": "en-AU-WilliamNeural",
    "female_au": "en-AU-NatashaNeural"
}
```

### Video Settings (Line ~50 in main.py)
```python
DEFAULT_DURATION = 60        # Video length in seconds
VIDEO_RESOLUTION = (1920, 1080)  # Full HD
FPS = 30                     # Frames per second
NUM_VIDEOS = 3               # Stock footage clips
```

---

## 🐛 Troubleshooting

### Common Issues

**1. `ModuleNotFoundError: No module named 'moviepy.editor'`**
```bash
pip install moviepy==1.0.3 Pillow==9.5.0
```

**2. `module 'PIL.Image' has no attribute 'ANTIALIAS'`**
```bash
pip uninstall Pillow
pip install Pillow==9.5.0
```

**3. API errors (401/403)**
- Check your API keys are correct
- Verify API quotas aren't exceeded

**4. Video creation fails**
- Ensure downloaded videos aren't corrupted
- Check available disk space (need ~100MB)

---

## 📝 Assignment Context

This project was created for an AI automation assignment with the following requirements:

- ✅ End-to-end automation (topic → video)
- ✅ Free tools only (Gemini, Edge TTS, Pexels, MoviePy)
- ✅ Bonus features (thumbnail, SEO, subtitles, upload prep)
- ✅ Complete documentation

**Deliverables:**
1. ✅ YouTube link (manual upload from generated video)
2. ✅ GitHub repository (this repo)
3. ✅ Screen recording (showing pipeline execution)
4. ✅ Write-up (see below)

---

## 📄 Project Write-up

### Tools Used

- **Gemini 2.5 Flash** - Script and SEO generation (free 15 RPM)
- **Edge TTS** - Text-to-speech (free, unlimited)
- **Pexels API** - Stock video footage (free 200 requests/hour)
- **MoviePy** - Video editing and assembly
- **Pillow (PIL)** - Image processing for thumbnails
- **Python 3.11.9** - Core programming language

### Biggest Challenge

The biggest challenge was handling **video synchronization and timing**. The pipeline needed to:
1. Calculate exact voiceover duration
2. Trim or loop stock footage to match audio length
3. Ensure seamless transitions between clips
4. Maintain consistent resolution (1920x1080) across different source videos

**Solution:** Implemented dynamic video processing that:
- Calculates words-per-second for timing
- Resizes and crops videos to target resolution
- Loops short clips or trims long ones
- Removes original audio to prevent conflicts

### What I'd Improve

1. **Smarter Visual Matching** - Use Gemini Vision API to analyze script content and fetch more contextually relevant footage
2. **Multiple Voice Styles** - Add emotion detection to match voice tone with content
3. **Advanced Editing** - Implement transitions, text overlays, and B-roll
4. **YouTube API Integration** - Automate the upload process with OAuth2
5. **Error Recovery** - Add checkpointing to resume failed pipelines
6. **Video Quality** - Implement scene detection for better clip selection
7. **Caching** - Store generated assets to avoid regeneration

### Time Breakdown

- Research & setup: 1 day
- Core pipeline (Steps 1-4): 2 days
- Bonus features: 2 days
- Testing & debugging: 1 day
- Documentation: 1 day

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more TTS providers (ElevenLabs, Google TTS)
- [ ] Implement custom transitions between clips
- [ ] Add background music support
- [ ] Support multiple languages
- [ ] Add video templates (intro/outro)
- [ ] Implement actual YouTube API upload
- [ ] Add progress bars for long operations

---

## 📜 License

MIT License - feel free to use for learning, projects, or commercial work.

---

## 🙏 AI and Site Details

- **Anthropic Claude** - AI assistance in development
- **Google Gemini** - Script and SEO generation
- **Pexels** - Free stock footage
- **Microsoft Edge TTS** - Natural voice synthesis

---

## 📞 Details

Created by Bhaskar Rana

- GitHub: @blackstag2k(https://github.com/yourusername)
- Email: ranaji2k@gmail.com





