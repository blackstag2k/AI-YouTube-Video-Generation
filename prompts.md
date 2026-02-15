# 🤖 AI Prompts Used in Pipeline

This document contains all AI prompts used in the video generation pipeline.

---

## 1️⃣ Script Generation Prompt

**Model:** Gemini 2.5 Flash  
**Location:** Step 1 - Generate Script  
**Purpose:** Create engaging YouTube video script
```
Create a {duration_seconds}-second YouTube video script about: {topic}

Requirements:
- Strong hook in the first 5 seconds to grab attention
- 3 clear main points with explanations
- Conversational, energetic tone
- Call to action at the end
- Approximately {target_words} words (for {duration_seconds} seconds at natural speaking pace)
- NO markdown, NO formatting, NO stage directions
- ONLY the narration text that will be spoken

Write the script now:
```

**Variables:**
- `{topic}` - User-provided video topic
- `{duration_seconds}` - Target video length (default: 60)
- `{target_words}` - Calculated as `duration_seconds * 2.5`

**Example Input:** "The science behind morning coffee"  
**Example Output:** "Ever wonder why that morning coffee hits different? Today we're diving into the fascinating science... [continues for ~150 words]"

---

## 2️⃣ Thumbnail Text Generation Prompt

**Model:** Gemini 2.5 Flash  
**Location:** Step 5 - Generate Thumbnail  
**Purpose:** Create catchy thumbnail text overlay
```
You are a YouTube thumbnail expert.

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
{
    "main_text": "your main text here",
    "subtitle": "optional subtitle or empty string"
}

No other text, just the JSON.
```

**Variables:**
- `{topic}` - Video topic
- `{script[:500]}` - First 500 characters of script

**Example Output:**
```json
{
    "main_text": "Coffee's Dark Secret",
    "subtitle": "Science Revealed"
}
```

---

## 3️⃣ SEO Metadata Generation Prompt

**Model:** Gemini 2.5 Flash  
**Location:** Step 6 - Generate SEO  
**Purpose:** Create YouTube-optimized metadata
```
You are a YouTube SEO expert.

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
{
    "title": "your optimized title",
    "description": "your full description",
    "tags": ["tag1", "tag2", "tag3", ...]
}

No other text, just the JSON.
```

**Variables:**
- `{topic}` - Video topic
- `{script}` - Complete video script

**Example Output:**
```json
{
    "title": "The Science Behind Your Morning Coffee ☕ (Mind-Blowing!)",
    "description": "Discover why your morning coffee works so well! In this video, we explore the neuroscience behind caffeine...",
    "tags": ["coffee science", "caffeine explained", "morning routine", "neuroscience", ...]
}
```

---

## 4️⃣ Pexels Video Search Query

**API:** Pexels Video Search  
**Location:** Step 3 - Fetch Visuals  
**Purpose:** Find relevant stock footage

**Query Format:**
```
{topic}
```

**Parameters:**
- `per_page`: 3-5 videos
- `orientation`: "landscape"
- `size`: Closest to 1920x1080

**Example Query:** "morning coffee steam"

---

## 5️⃣ Pexels Image Search Query (Thumbnail)

**API:** Pexels Photo Search  
**Location:** Step 5 - Generate Thumbnail  
**Purpose:** Find background image for thumbnail

**Query Format:**
```
{topic}
```

**Parameters:**
- `per_page`: 5 images
- `orientation`: "landscape"
- `quality`: "large2x" (high resolution)

**Example Query:** "coffee beans close up"

---

## 📊 Prompt Engineering Insights

### What Worked Well

1. **Explicit Format Constraints**
   - Specifying "NO markdown, NO formatting" prevented parsing issues
   - Requesting "ONLY JSON" ensured clean output

2. **Concrete Numbers**
   - "3-5 words MAX" is better than "short text"
   - "150-200 words" is better than "moderate length"

3. **Context Provision**
   - Giving script preview helped generate relevant thumbnails
   - Full script context improved SEO quality

### What Could Be Improved

1. **Few-Shot Examples**
   - Adding 2-3 examples of good outputs would improve consistency

2. **Negative Prompting**
   - Explicitly state what NOT to include (e.g., "No clickbait")

3. **Chain-of-Thought**
   - Ask model to explain reasoning before generating final output

---

## 🔧 Prompt Customization Guide

### Adjusting Script Tone

Change this line in Script Generation:
```
- Conversational, energetic tone
```

To:
```
- Professional, authoritative tone
- Casual, humorous tone
- Educational, informative tone
```

### Changing Thumbnail Style

Modify power words list:
```
- Use power words (Amazing, Secret, Shocking, Ultimate, etc.)
```

To:
```
- Use professional words (Expert, Guide, Essential, Complete, etc.)
- Use curiosity words (Hidden, Unknown, Revealed, Truth, etc.)
```

### SEO Targeting

Add keyword constraints:
```
Requirements for TITLE:
- 60 characters or less
- Include main keyword: "{primary_keyword}"
- Include secondary keyword: "{secondary_keyword}"
```

---

## 📝 Prompt Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01 | Initial prompts |
| 1.1 | 2024-02 | Added JSON format requirement |
| 1.2 | 2024-02 | Removed markdown escaping issues |

---

**Note:** All prompts are designed for Gemini 2.5 Flash model. Adaptation may be needed for other LLMs.