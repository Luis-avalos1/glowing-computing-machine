#!/usr/bin/env python3
# AI Shorts Generator - Main Script
# Complete architecture with modular design for different AI providers

import os
import sys
import json
import time
import argparse
import subprocess
import random
import math
from pathlib import Path
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("shorts_generator.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ShortsGenerator")

print("🎬 AI Shorts Generator 🎬")
print("Create YouTube Shorts videos from text prompts")
print("---------------------------------------------")

# ===============================
# Auto-Install Dependencies
# ===============================

def check_and_install_dependencies():
    """Check for required libraries and install them if missing"""
    logger.info("Checking for required dependencies...")
    
    required_packages = [
        "requests",
        "gtts",
        "pillow",
        "ffmpeg-python"
    ]
    
    missing_packages = []
    
    # Check which packages are missing
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✓ {package} is already installed")
        except ImportError:
            missing_packages.append(package)
            logger.info(f"✗ {package} needs to be installed")
    
    # Install missing packages
    if missing_packages:
        logger.info("Installing missing packages...")
        for package in missing_packages:
            logger.info(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError:
                logger.error(f"✗ Failed to install {package}. Please install it manually.")
                logger.info(f"   pip install {package}")
        logger.info("All required packages installed successfully!")
    else:
        logger.info("All required packages are already installed!")
    
    # Now import the packages (they should be installed)
    global requests, Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
    import requests
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

# Run dependency check and installation
check_and_install_dependencies()

# ===============================
# Core Configuration
# ===============================

# Create necessary directories
TEMP_DIR = Path("temp")
OUTPUT_DIR = Path("output")
ASSETS_DIR = Path("assets")
CONFIG_DIR = Path("config")

# Create directories if they don't exist
for directory in [TEMP_DIR, OUTPUT_DIR, ASSETS_DIR, CONFIG_DIR]:
    directory.mkdir(exist_ok=True)
    logger.info(f"✓ Ensured {directory} directory exists")

# Create assets subfolders
STOCK_VIDEOS_DIR = ASSETS_DIR / "videos"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

for directory in [STOCK_VIDEOS_DIR, MUSIC_DIR, FONTS_DIR]:
    directory.mkdir(exist_ok=True)

# Load configuration if exists
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_CONFIG = {
    "ai_provider": "simulated_ai",  # Default to most compatible option
    "ai_providers": [
        {"name": "local_stable_diffusion", "priority": 1, "url": "http://127.0.0.1:7860"},
        {"name": "huggingface", "priority": 2},
        {"name": "stable_diffusion_online", "priority": 3},
        {"name": "simulated_ai", "priority": 4}
    ],
    "visual_styles": {
        "educational": {
            "prompt_prefix": "educational, informative, clear, professional",
            "negative_prompt": "blurry, low quality, text overlay"
        },
        "vibrant": {
            "prompt_prefix": "vibrant, colorful, eye-catching, trending",
            "negative_prompt": "dull, boring, monotone"
        }
    },
    "default_style": "educational",
    "voices": {
        "male1": {
            "provider": "gtts",
            "language": "en",
            "options": {"tld": "com", "slow": false}
        },
        "female1": {
            "provider": "gtts",
            "language": "en-uk",
            "options": {"tld": "co.uk", "slow": false}
        }
    },
    "default_voice": "male1"
}

# Create default config if it doesn't exist
if not CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    logger.info(f"Created default configuration at {CONFIG_FILE}")

# Load config
try:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    logger.info(f"Loaded configuration from {CONFIG_FILE}")
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.info("Using default configuration")
    config = DEFAULT_CONFIG

# ===============================
# Script Generator Module
# ===============================

class ScriptGenerator:
    """Generates scripts for YouTube Shorts from text prompts"""
    
    def __init__(self, templates_dir=None):
        """Initialize the script generator with templates"""
        self.templates_dir = templates_dir or Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Default templates
        self.hook_templates = [
            "Want to know the truth about {}?",
            "This {} trick will blow your mind!",
            "You won't believe what happens with {}!",
            "Here's why {} is changing everything",
            "The {} secret nobody is talking about",
            "Top 5 things about {} you never knew",
            "How {} can transform your results",
            "The shocking truth about {}",
            "Why everyone is talking about {} right now",
            "I tried {} for a week and here's what happened"
        ]
        
        self.section_templates = [
            "First, let's talk about the importance of {}.",
            "Did you know that {} can improve your results by 80%?",
            "Here's why {} matters more than you think.",
            "The best part about {} is how simple it is.",
            "Many people overlook {} but it's crucial for success.",
            "Experts agree that {} is a game-changer.",
            "Research shows that {} can make a huge difference.",
            "I've found that {} works best when you're consistent.",
            "The secret to mastering {} is practice.",
            "When it comes to {}, timing is everything."
        ]
        
        self.cta_templates = [
            "Like and follow for more tips!",
            "Comment below if you want to learn more!",
            "Try this today and let me know your results!",
            "Share this with someone who needs to see it!",
            "Subscribe for daily content like this!",
            "Hit that like button if you found this helpful!",
            "Don't forget to follow for more content!",
            "Want more tips? Hit subscribe now!",
            "Let me know in the comments what you think!",
            "Tag a friend who needs to see this!"
        ]
        
        # Load custom templates if they exist
        self._load_custom_templates()
    
    def _load_custom_templates(self):
        """Load custom templates from files if they exist"""
        for template_type in ["hook", "section", "cta"]:
            template_file = self.templates_dir / f"{template_type}_templates.txt"
            if template_file.exists():
                try:
                    with open(template_file, 'r') as f:
                        templates = [line.strip() for line in f if line.strip()]
                    
                    if templates:
                        if template_type == "hook":
                            self.hook_templates = templates
                        elif template_type == "section":
                            self.section_templates = templates
                        elif template_type == "cta":
                            self.cta_templates = templates
                        
                        logger.info(f"Loaded custom {template_type} templates from {template_file}")
                except Exception as e:
                    logger.error(f"Error loading {template_type} templates: {e}")
    
    def generate_script(self, prompt):
        """Generate a script from a prompt"""
        logger.info(f"Generating script for prompt: {prompt}")
        
        script = {
            "hook": self._generate_hook(prompt),
            "sections": self._generate_sections(prompt),
            "cta": self._generate_cta(prompt),
            "estimated_duration": 45
        }
        
        # Save script to file
        script_file = TEMP_DIR / "script.json"
        with open(script_file, 'w') as f:
            json.dump(script, f, indent=2)
            
        logger.info(f"Script saved to {script_file}")
        
        # Display the script
        logger.info("\nGenerated Script:")
        logger.info(f"Hook: {script['hook']}")
        for i, section in enumerate(script['sections'], 1):
            logger.info(f"Section {i}: {section}")
        logger.info(f"Call to Action: {script['cta']}")
        logger.info(f"Estimated Duration: {script['estimated_duration']} seconds")
        
        return script
    
    def _generate_hook(self, prompt):
        """Generate an attention-grabbing hook based on the prompt"""
        # Extract key words from prompt
        words = prompt.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in 
                    ['this', 'that', 'with', 'from', 'about', 'would', 'could', 'should']]
        
        # Select a keyword and template
        if keywords:
            keyword = random.choice(keywords)
            hook = random.choice(self.hook_templates).format(keyword)
        else:
            hook = random.choice(self.hook_templates).format("this")
            
        return hook
    
    def _generate_sections(self, prompt):
        """Generate main content sections based on the prompt"""
        # Extract potential topics from prompt
        words = prompt.lower().split()
        potential_topics = [word for word in words if len(word) > 3]
        
        # Generate 3-5 sections
        num_sections = random.randint(3, 5)
        sections = []
        
        for i in range(num_sections):
            if potential_topics:
                topic = random.choice(potential_topics)
                section = random.choice(self.section_templates).format(topic)
            else:
                section = random.choice(self.section_templates).format("this technique")
            sections.append(section)
            
        return sections
    
    def _generate_cta(self, prompt):
        """Generate a call-to-action based on the prompt"""
        return random.choice(self.cta_templates)

# ===============================
# AI Provider Interface
# ===============================

class AIProvider:
    """Base class for AI providers"""
    
    @staticmethod
    def get_provider(provider_name, config):
        """Factory method to get the appropriate provider"""
        if provider_name == "local_stable_diffusion":
            return LocalStableDiffusionProvider(config)
        elif provider_name == "huggingface":
            return HuggingFaceProvider(config)
        elif provider_name == "stable_diffusion_online":
            return StableDiffusionOnlineProvider(config)
        elif provider_name == "simulated_ai":
            return SimulatedAIProvider(config)
        else:
            logger.warning(f"Unknown provider: {provider_name}, falling back to simulated AI")
            return SimulatedAIProvider(config)
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=912):
        """Generate an image from a prompt"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def generate_video(self, image_path, motion_prompt, duration=5.0):
        """Generate a video from an image and motion prompt"""
        raise NotImplementedError("Subclasses must implement this method")

class LocalStableDiffusionProvider(AIProvider):
    """Provider for local Stable Diffusion instance"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.sd_url = config.get("ai_providers", [])[0].get("url", "http://127.0.0.1:7860")
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=912):
        """Generate an image using local Stable Diffusion"""
        logger.info(f"Generating image with local Stable Diffusion: {prompt}")
        
        try:
            import requests
            import base64
            import io
            from PIL import Image
            
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": 30,
                "width": width,
                "height": height,
                "sampler_name": "DPM++ 2M Karras",
                "cfg_scale": 7,
                "seed": -1  # Random seed
            }
            
            response = requests.post(f"{self.sd_url}/sdapi/v1/txt2img", json=payload)
            if response.status_code == 200:
                        r = response.json()
                        image_data = r["images"][0]
                        
                        # Decode base64 image
                        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))
                        
                        # Save the image
                        image_path = TEMP_DIR / f"generated_image_{int(time.time())}.png"
                        image.save(image_path)
                        
                        logger.info(f"Image saved to {image_path}")
                        return str(image_path)
            else:
                        logger.error(f"Error: Received status code {response.status_code}")
                        return None
                    
        except Exception as e:
                logger.error(f"Error generating image with local Stable Diffusion: {e}")
                return None
            
    def generate_video(self, image_path, motion_prompt, duration=5.0):
        """Generate a video using local Stable Video Diffusion"""
        logger.info(f"Generating video with local Stable Video Diffusion: {motion_prompt}")
        
        try:
            import requests
            import base64
            
            # Read the source image
            with open(image_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            payload = {
                "image": img_base64,
                "prompt": motion_prompt,
                "negative_prompt": "shaky, blurry, low quality",
                "fps": 24,
                "num_frames": min(25, int(duration * 8)),  # SVD supports max 25 frames
                "motion_bucket_id": 40,  # Higher = more motion
                "cond_aug": 0.02,
            }
            
            response = requests.post(f"{self.sd_url}/sdapi/v1/img2video", json=payload)
            
            if response.status_code == 200:
                r = response.json()
                video_path = r.get("video")
                
                if video_path:
                    # If the API returns a path, use it
                    return video_path
                elif "video_bytes" in r:
                    # If the API returns the video data, save it
                    video_bytes = base64.b64decode(r["video_bytes"])
                    video_path = TEMP_DIR / f"generated_video_{int(time.time())}.mp4"
                    
                    with open(video_path, "wb") as f:
                        f.write(video_bytes)
                    
                    return str(video_path)
                else:
                    logger.error("No video data in response")
                    return None
            else:
                logger.error(f"Error: Received status code {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating video with local Stable Video Diffusion: {e}")
            return None
        
class HuggingFaceProvider(AIProvider):
    """Provider for Hugging Face's inference API"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.api_token = os.environ.get("HUGGINGFACE_TOKEN", "")
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=912):
        """Generate an image using Hugging Face's inference API"""
        logger.info(f"Generating image with Hugging Face: {prompt}")
        
        try:
            import requests
            import io
            from PIL import Image
            
            # Using runwayml/stable-diffusion-v1-5 model which is available for free
            API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                    "width": width,
                    "height": height
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                # The API returns the image directly
                image = Image.open(io.BytesIO(response.content))
                
                # Save the image
                image_path = TEMP_DIR / f"hf_generated_image_{int(time.time())}.png"
                image.save(image_path)
                
                logger.info(f"Image saved to {image_path}")
                return str(image_path)
            else:
                logger.error(f"Error: Received status code {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image with Hugging Face: {e}")
            return None
    
    def generate_video(self, image_path, motion_prompt, duration=5.0):
        """Generate a video using Hugging Face's inference API"""
        logger.info(f"Generating video with Hugging Face not fully implemented.")
        logger.info(f"Using static image for video segment instead.")
        
        # This is a placeholder - we'll just use the image as is
        # In a real implementation, you would call Hugging Face's Stable Video Diffusion endpoint
        return image_path

class StableDiffusionOnlineProvider(AIProvider):
    """Provider for free online Stable Diffusion services"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        # No specific configuration needed
        pass
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=912):
        """Generate an image using free online Stable Diffusion services"""
        logger.info(f"Generating image with online Stable Diffusion: {prompt}")
        
        try:
            import requests
            import io
            from PIL import Image
            
            # There are several free online services, this is an example
            # Note: Some services might change their API or require registration
            API_URL = "https://stablediffusionapi.com/api/v3/text2img"
            
            payload = {
                "key": "demo",  # Using demo key for example purposes
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": str(width),
                "height": str(height),
                "samples": "1",
                "num_inference_steps": "30",
                "guidance_scale": 7.5,
                "safety_checker": "yes"
            }
            
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                r = response.json()
                if "output" in r and len(r["output"]) > 0:
                    image_url = r["output"][0]
                    # Download the image
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        
                        # Save the image
                        image_path = TEMP_DIR / f"online_generated_image_{int(time.time())}.png"
                        image.save(image_path)
                        
                        logger.info(f"Image saved to {image_path}")
                        return str(image_path)
                
                logger.error("API responded but no image was returned")
                return None
            else:
                logger.error(f"Error: Received status code {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image with online Stable Diffusion: {e}")
            return None
    
    def generate_video(self, image_path, motion_prompt, duration=5.0):
        """Online video generation is not implemented in the free tier"""
        logger.info(f"Online video generation not available in free tier.")
        logger.info(f"Using static image for video segment instead.")
        
        # Just return the image path since we can't generate a video
        return image_path

class SimulatedAIProvider(AIProvider):
    """Provider that simulates AI generation using basic image processing"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        # No specific configuration needed
        pass
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=912):
        """Generate a simulated AI image using PIL effects"""
        logger.info(f"Generating simulated AI image: {prompt}")
        
        try:
            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
            import random
            import math
            
            # Create a base image
            img = Image.new('RGB', (width, height), color='black')
            draw = ImageDraw.Draw(img)
            
            # Extract color from prompt
            colors = {
                'happy': '#FFD700',  # Gold
                'sad': '#4682B4',    # SteelBlue
                'angry': '#FF4500',  # OrangeRed
                'calm': '#20B2AA',   # LightSeaGreen
                'nature': '#228B22', # ForestGreen
                'tech': '#1E90FF',   # DodgerBlue
                'love': '#FF1493',   # DeepPink
                'dark': '#2F4F4F',   # DarkSlateGray
                'light': '#F5F5F5',  # WhiteSmoke
            }
            
            # Determine dominant color based on prompt
            dominant_color = '#1E90FF'  # Default blue
            for keyword, color in colors.items():
                if keyword in prompt.lower():
                    dominant_color = color
                    break
            
            # Extract style from prompt
            abstract = 'abstract' in prompt.lower() or 'art' in prompt.lower()
            landscape = 'landscape' in prompt.lower() or 'nature' in prompt.lower()
            portrait = 'portrait' in prompt.lower() or 'person' in prompt.lower()
            
            # Generate base gradient
            for y in range(height):
                r, g, b = self._hex_to_rgb(dominant_color)
                # Add variation based on position
                if landscape:
                    # Horizon effect
                    horizon = height * 0.7
                    if y < horizon:
                        # Sky
                        factor = 1 - (y / horizon) * 0.5
                        r = int(r * factor)
                        g = int(g * factor)
                        b = min(255, int(b * (1 + factor * 0.2)))
                    else:
                        # Ground
                        factor = (y - horizon) / (height - horizon)
                        r = int(r * (0.7 - factor * 0.3))
                        g = int(g * (0.7 - factor * 0.2))
                        b = int(b * (0.7 - factor * 0.4))
                elif portrait:
                    # Vignette effect
                    center_y = height // 2
                    distance = abs(y - center_y) / (height // 2)
                    factor = 1 - distance * 0.5
                    r = int(r * factor)
                    g = int(g * factor)
                    b = int(b * factor)
                elif abstract:
                    # Random color shifts
                    factor = 0.7 + 0.3 * math.sin(y / 30)
                    r = min(255, int(r * factor))
                    g = min(255, int(g * factor * 0.8 + 0.2 * math.cos(y / 20)))
                    b = min(255, int(b * factor * 0.9 + 0.1 * math.sin(y / 40)))
                
                # Draw horizontal line with calculated color
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add some shapes based on prompt
            for _ in range(50):
                shape_x = random.randint(0, width)
                shape_y = random.randint(0, height)
                shape_size = random.randint(5, 100)
                shape_color = self._adjust_color(dominant_color, 0.8 + random.random() * 0.4)
                
                if abstract:
                    # Random shapes for abstract
                    shape_type = random.choice(['circle', 'rectangle', 'line'])
                    if shape_type == 'circle':
                        draw.ellipse(
                            [shape_x - shape_size//2, shape_y - shape_size//2, 
                             shape_x + shape_size//2, shape_y + shape_size//2], 
                            fill=shape_color, outline=None
                        )
                    elif shape_type == 'rectangle':
                        draw.rectangle(
                            [shape_x - shape_size//2, shape_y - shape_size//2, 
                             shape_x + shape_size//2, shape_y + shape_size//2],
                            fill=shape_color, outline=None
                        )
                    else:  # line
                        angle = random.random() * 2 * math.pi
                        length = shape_size * 2
                        end_x = shape_x + int(math.cos(angle) * length)
                        end_y = shape_y + int(math.sin(angle) * length)
                        draw.line([shape_x, shape_y, end_x, end_y], 
                                  fill=shape_color, width=random.randint(1, 5))
                
                elif landscape:
                    # Add landscape elements
                    horizon = height * 0.7
                    if shape_y > horizon:
                        # Ground elements (rocks, bushes)
                        if random.random() < 0.3:
                            # Rock
                            draw.ellipse(
                                [shape_x - shape_size//4, shape_y - shape_size//8, 
                                 shape_x + shape_size//4, shape_y + shape_size//8],
                                fill=self._adjust_color('#808080', 0.7 + random.random() * 0.6)
                            )
                        else:
                            # Bush
                            bush_color = self._adjust_color('#228B22', 0.7 + random.random() * 0.6)
                            for _ in range(5):
                                bush_x = shape_x + random.randint(-shape_size//3, shape_size//3)
                                bush_y = shape_y + random.randint(-shape_size//3, shape_size//3)
                                bush_size = shape_size // 2
                                draw.ellipse(
                                    [bush_x - bush_size//2, bush_y - bush_size//2,
                                     bush_x + bush_size//2, bush_y + bush_size//2],
                                    fill=bush_color
                                )
                    else:
                        # Sky elements (clouds, birds)
                        if random.random() < 0.7:
                            # Cloud
                            cloud_color = self._adjust_color('#FFFFFF', 0.7 + random.random() * 0.3)
                            for _ in range(5):
                                cloud_x = shape_x + random.randint(-shape_size, shape_size)
                                cloud_y = shape_y + random.randint(-shape_size//2, shape_size//2)
                                cloud_size = shape_size
                                draw.ellipse(
                                    [cloud_x - cloud_size//2, cloud_y - cloud_size//4,
                                     cloud_x + cloud_size//2, cloud_y + cloud_size//4],
                                    fill=cloud_color
                                )
                        else:
                            # Bird (simple V shape)
                            bird_color = '#000000'
                            wing_size = shape_size // 4
                            draw.line(
                                [shape_x - wing_size, shape_y - wing_size,
                                 shape_x, shape_y,
                                 shape_x + wing_size, shape_y - wing_size],
                                fill=bird_color, width=2
                            )
                
                elif portrait:
                    # Create abstract portrait-like elements
                    if random.random() < 0.2 and shape_y > height//3 and shape_y < 2*height//3:
                        # Face-like shape in center area
                        face_color = self._adjust_color('#FFC0CB', 0.8 + random.random() * 0.4)
                        face_size = shape_size * 2
                        draw.ellipse(
                            [shape_x - face_size//2, shape_y - face_size//1.5,
                             shape_x + face_size//2, shape_y + face_size//1.5],
                            fill=face_color
                        )
                        
                        # Eyes
                        eye_size = face_size // 8
                        eye_color = '#FFFFFF'
                        pupil_color = '#000000'
                        
                        # Left eye
                        left_eye_x = shape_x - face_size//5
                        eye_y = shape_y - face_size//6
                        draw.ellipse(
                            [left_eye_x - eye_size, eye_y - eye_size//2,
                             left_eye_x + eye_size, eye_y + eye_size//2],
                            fill=eye_color
                        )
                        draw.ellipse(
                            [left_eye_x - eye_size//3, eye_y - eye_size//3,
                             left_eye_x + eye_size//3, eye_y + eye_size//3],
                            fill=pupil_color
                        )
                        
                        # Right eye
                        right_eye_x = shape_x + face_size//5
                        draw.ellipse(
                            [right_eye_x - eye_size, eye_y - eye_size//2,
                             right_eye_x + eye_size, eye_y + eye_size//2],
                            fill=eye_color
                        )
                        draw.ellipse(
                            [right_eye_x - eye_size//3, eye_y - eye_size//3,
                             right_eye_x + eye_size//3, eye_y + eye_size//3],
                            fill=pupil_color
                        )
            
            # Apply some filters for a more "AI-generated" look
            
            # 1. Add some noise
            noise_img = Image.new('RGB', (width, height), color='black')
            noise_draw = ImageDraw.Draw(noise_img)
            
            for x in range(0, width, 2):
                for y in range(0, height, 2):
                    noise_value = random.randint(0, 15)
                    noise_draw.point((x, y), fill=(noise_value, noise_value, noise_value))
            
            img = ImageChops.add(img, noise_img)
            
            # 2. Slight blur for smoothness
            img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
            
            # 3. Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            
            # Save the image
            image_path = TEMP_DIR / f"simulated_ai_image_{int(time.time())}.jpg"
            img.save(image_path, quality=95)
            
            logger.info(f"Simulated AI image saved to {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"Error creating simulated AI image: {e}")
            return None
    
    def generate_video(self, image_path, motion_prompt, duration=5.0):
        """Generate a simulated video using simple animations"""
        logger.info(f"Generating simulated AI video: {motion_prompt}")
        
        try:
            # Get parameters from the motion prompt
            zoom = "zoom" in motion_prompt.lower()
            pan = "pan" in motion_prompt.lower()
            direction = None
            
            if "left" in motion_prompt.lower():
                direction = "left"
            elif "right" in motion_prompt.lower():
                direction = "right"
            elif "up" in motion_prompt.lower():
                direction = "up"
            elif "down" in motion_prompt.lower():
                direction = "down"
            
            # Create temp directory for frames
            temp_dir = Path(tempfile.mkdtemp())
            
            # Parameters
            fps = 24
            total_frames = int(duration * fps)
            
            # Open the source image
            from PIL import Image
            source_img = Image.open(image_path)
            width, height = source_img.size
            
            # Generate frames
            for frame in range(total_frames):
                # Copy the source image
                progress = frame / total_frames
                
                # Apply motion effects
                if zoom:
                    # Zoom effect
                    zoom_factor = 1.0 + (progress * 0.2)  # Zoom in 20%
                    
                    # Calculate new dimensions
                    new_width = int(width * zoom_factor)
                    new_height = int(height * zoom_factor)
                    
                    # Resize the image
                    resized = source_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Crop back to original size from center
                    left = (new_width - width) // 2
                    top = (new_height - height) // 2
                    frame_img = resized.crop((left, top, left + width, top + height))
                    
                elif pan and direction:
                    # Pan effect
                    # Create larger image for panning
                    pan_img = Image.new('RGB', (width * 2, height * 2), color='black')
                    pan_img.paste(source_img, (width // 2, height // 2))
                    
                    # Calculate pan offset
                    max_offset = width // 4  # 25% of width
                    offset = int(progress * max_offset)
                    
                    # Apply direction
                    if direction == "left":
                        left = width // 2 + offset
                        top = height // 2
                    elif direction == "right":
                        left = width // 2 - offset
                        top = height // 2
                    elif direction == "up":
                        left = width // 2
                        top = height // 2 + offset
                    elif direction == "down":
                        left = width // 2
                        top = height // 2 - offset
                    else:
                        left = width // 2
                        top = height // 2
                    
                    # Crop to original size
                    frame_img = pan_img.crop((left, top, left + width, top + height))
                    
                else:
                    # No motion, just subtle animation
                    frame_img = source_img.copy()
                    
                    # Add subtle pulsing effect
                    brightness = 0.9 + 0.2 * math.sin(progress * math.pi * 2)
                    enhancer = ImageEnhance.Brightness(frame_img)
                    frame_img = enhancer.enhance(brightness)
                
                # Save frame
                frame_path = temp_dir / f"frame_{frame:04d}.jpg"
                frame_img.save(frame_path, quality=95)
            
            # Use FFmpeg to convert frames to video
            video_path = TEMP_DIR / f"simulated_video_{int(time.time())}.mp4"
            
            try:
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(fps),
                    "-i", f"{temp_dir}/frame_%04d.jpg",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-crf", "23",
                    str(video_path)
                ]
                subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info(f"Simulated AI video saved to {video_path}")
                return str(video_path)
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.warning("FFmpeg not found, returning path to frame directory")
                return str(temp_dir)
                
        except Exception as e:
            logger.error(f"Error creating simulated AI video: {e}")
            return None
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _adjust_color(self, hex_color, factor):
        """Adjust color brightness by factor (>1 brighter, <1 darker)"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

# ===============================
# Audio Generator Module
# ===============================

class AudioGenerator:
    """Generates audio for YouTube Shorts"""
    
    def __init__(self, config=None):
        """Initialize audio generator with configuration"""
        self.config = config or {}
        self.voices = self.config.get("voices", {
            "male1": {"provider": "gtts", "language": "en", "options": {"tld": "com", "slow": False}},
            "female1": {"provider": "gtts", "language": "en-uk", "options": {"tld": "co.uk", "slow": False}}
        })
        self.default_voice = self.config.get("default_voice", "male1")
    
    def generate_voiceover(self, script, voice_type=None):
        """Generate a voiceover from a script"""
        voice_type = voice_type or self.default_voice
        voice_config = self.voices.get(voice_type, self.voices[self.default_voice])
        
        logger.info(f"Generating voiceover with voice: {voice_type}")
        
        # Combine script sections into full text
        full_text = script["hook"] + " "
        for section in script["sections"]:
            full_text += section + " "
        full_text += script["cta"]
        
        # Generate based on provider
        provider = voice_config.get("provider", "gtts")
        
        if provider == "gtts":
            return self._generate_with_gtts(full_text, voice_config)
        else:
            logger.warning(f"Unknown TTS provider: {provider}, falling back to gTTS")
            return self._generate_with_gtts(full_text)
    
    def _generate_with_gtts(self, text, voice_config=None):
        """Generate audio using Google Text-to-Speech"""
        try:
            from gtts import gTTS
            
            # Get voice settings
            options = {}
            if voice_config:
                language = voice_config.get("language", "en")
                options = voice_config.get("options", {})
            else:
                language = "en"
            
            # Generate TTS audio
            audio_file = TEMP_DIR / f"voiceover_{int(time.time())}.mp3"
            tts = gTTS(text=text, lang=language, **options)
            tts.save(str(audio_file))
            
            logger.info(f"Voiceover saved to {audio_file}")
            return str(audio_file)
            
        except Exception as e:
            logger.error(f"Error generating voiceover with gTTS: {e}")
            return None
    
    def find_background_music(self, mood="upbeat", duration=60):
        """Find appropriate background music"""
        logger.info(f"Finding {mood} background music")
        
        # Check if we have any music files in the music directory
        music_files = list(MUSIC_DIR.glob("*.mp3"))
        if not music_files:
            logger.warning("No music files found in assets/music directory.")
            logger.info("Creating a placeholder music file...")
            
            # Create placeholder music file
            music_path = TEMP_DIR / f"background_music_{int(time.time())}.mp3"
            with open(music_path, 'w') as f:
                f.write("Simulated music file")
                
            return str(music_path)
        
        # Try to find music matching the requested mood
        matching_music = [f for f in music_files if mood.lower() in f.name.lower()]
        
        if matching_music:
            music_path = str(random.choice(matching_music))
        else:
            music_path = str(random.choice(music_files))
        
        logger.info(f"Selected music: {os.path.basename(music_path)}")
        return music_path

# ===============================
# Caption Generator Module
# ===============================

class CaptionGenerator:
    """Generates captions for YouTube Shorts"""
    
    def __init__(self):
        """Initialize caption generator"""
        pass
    
    def generate_captions(self, script, audio_path=None):
        """Generate timed captions for the video"""
        logger.info("Generating captions...")
        
        # Simplified caption timing - in reality, would sync with audio
        captions = []
        current_time = 0
        
        # Estimate words per second
        wps = 2.5
        
        # Add caption for hook
        words = len(script["hook"].split())
        duration = words / wps
        captions.append({
            "text": script["hook"],
            "start_time": current_time,
            "end_time": current_time + duration
        })
        current_time += duration
        
        # Add captions for sections
        for section in script["sections"]:
            words = len(section.split())
            duration = words / wps
            captions.append({
                "text": section,
                "start_time": current_time,
                "end_time": current_time + duration
            })
            current_time += duration
        
        # Add caption for CTA
        words = len(script["cta"].split())
        duration = words / wps
        captions.append({
            "text": script["cta"],
            "start_time": current_time,
            "end_time": current_time + duration
        })
        
        # Save captions as JSON (could also save as SRT or WebVTT)
        captions_file = TEMP_DIR / f"captions_{int(time.time())}.json"
        with open(captions_file, 'w') as f:
            json.dump(captions, f, indent=2)
        
        logger.info(f"Captions saved to {captions_file}")
        return captions


# ===============================
# Video Composer Module
# ===============================

class VideoComposer:
    """Composes the final video with all elements"""
    
    def __init__(self):
        """Initialize video composer"""
        # Check if FFmpeg is available
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            logger.info("✓ FFmpeg is installed!")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("✗ FFmpeg not found. Video composition will be limited.")
            return False
    
    def compose_video(self, visual_assets, audio_path, captions, output_path=None):
        """
        Compose the final video with all elements
        
        Args:
            visual_assets: List of visual assets (images or videos)
            audio_path: Path to voiceover audio
            captions: List of caption dictionaries
            output_path: Path to save the output video
            
        Returns:
            Path to the output video
        """
        if output_path is None:
            output_path = OUTPUT_DIR / f"shorts_{int(time.time())}.mp4"
        
        logger.info(f"Composing final video to {output_path}...")
        
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not available. Creating a description of the video instead.")
            # Create a text description of the video
            description = self._create_video_description(visual_assets, captions)
            description_path = str(output_path).replace(".mp4", ".txt")
            with open(description_path, 'w') as f:
                f.write(description)
            return description_path
        
        # Generate a file with a list of segments
        segments_file = TEMP_DIR / "segments.txt"
        segment_paths = []
        
        # Process each visual asset
        for i, asset in enumerate(visual_assets):
            asset_path = asset["path"]
            caption_text = asset.get("text", "")
            
            # Find corresponding caption
            caption = next((c for c in captions if c["text"] == caption_text), None)
            
            # Create a segment with the visual and caption
            segment_path = self._create_segment(
                asset_path, 
                caption_text, 
                segment_duration=asset.get("duration", 5.0),
                segment_index=i
            )
            
            if segment_path:
                segment_paths.append(segment_path)
        
        # If no segments were created, return None
        if not segment_paths:
            logger.error("No video segments could be created.")
            return None
        
        # Create a file with the list of segments
        with open(segments_file, 'w') as f:
            for segment in segment_paths:
                f.write(f"file '{segment}'\n")
        
        # Combine segments
        try:
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(segments_file),
                "-i", audio_path,  # Add the voiceover audio
                "-c:v", "copy",
                "-c:a", "aac",     # Audio codec
                "-map", "0:v",     # Map video from the first input (concatenated videos)
                "-map", "1:a",     # Map audio from the second input (voiceover)
                "-shortest",       # End when the shortest input ends
                str(output_path)
            ]
            
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"✓ Final video saved to {output_path}")
            return str(output_path)
        except subprocess.SubprocessError as e:
            logger.error(f"Error combining segments: {e}")
            return None
    
    def _create_segment(self, visual_path, caption_text, segment_duration=5.0, segment_index=0):
        """Create a video segment with caption overlay"""
        # Determine if the visual is an image or video
        is_image = not visual_path.endswith(('.mp4', '.mov', '.avi', '.mkv'))
        
        segment_path = TEMP_DIR / f"segment_{segment_index}_{int(time.time())}.mp4"
        
        try:
            if is_image:
                # Convert image to video segment
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-loop", "1",                   # Loop the image
                    "-i", visual_path,              # Input image
                    "-t", str(segment_duration),    # Duration
                    "-vf", f"drawtext=text='{caption_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=h-th-20",  # Add caption
                    "-c:v", "libx264",              # Video codec
                    "-pix_fmt", "yuv420p",          # Pixel format for compatibility
                    str(segment_path)
                ]
            else:
                # Process video segment
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", visual_path,              # Input video
                    "-vf", f"drawtext=text='{caption_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=h-th-20",  # Add caption
                    "-c:v", "libx264",              # Video codec
                    "-c:a", "copy",                 # Copy audio (if present)
                    str(segment_path)
                ]
            
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"✓ Created segment {segment_index}")
            return str(segment_path)
        except subprocess.SubprocessError as e:
            logger.error(f"Error creating segment {segment_index}: {e}")
            return None
    
    def _create_video_description(self, visual_assets, captions):
        """Create a text description of the video (fallback when FFmpeg is not available)"""
        description = "VIDEO DESCRIPTION (FFmpeg not available)\n"
        description += "===========================================\n\n"
        
        for i, asset in enumerate(visual_assets):
            description += f"SEGMENT {i+1}:\n"
            description += f"Visual: {asset['type']} - {os.path.basename(asset['path'])}\n"
            description += f"Text: {asset.get('text', 'No text')}\n"
            description += f"Duration: {asset.get('duration', 5.0)} seconds\n\n"
        
        description += "===========================================\n"
        description += "To create the actual video, please install FFmpeg:\n"
        description += "- Windows: https://ffmpeg.org/download.html\n"
        description += "- macOS: brew install ffmpeg\n"
        description += "- Linux: sudo apt install ffmpeg\n"
        
        return description

# ===============================
# Main Application Class
# ===============================

class AIShortsGenerator:
    """Main application class for generating YouTube Shorts"""
    
    def __init__(self, config=None):
        """Initialize the shorts generator with configuration"""
        self.config = config or {}
        
        # Create component instances
        self.script_generator = ScriptGenerator()
        self.audio_generator = AudioGenerator(self.config)
        self.caption_generator = CaptionGenerator()
        self.video_composer = VideoComposer()
        
        # Determine which AI provider to use
        provider_name = self.config.get("ai_provider", "simulated_ai")
        self.ai_provider = AIProvider.get_provider(provider_name, self.config)
        
        logger.info(f"Using AI provider: {provider_name}")
    
    def generate_video_from_prompt(self, prompt, output_path=None, style=None):
        """
        Generate a complete YouTube Short from a text prompt
        
        Args:
            prompt: Text prompt describing the video
            output_path: Path to save the output video
            style: Visual style to use
            
        Returns:
            Path to the generated video
        """
        if output_path is None:
            output_path = OUTPUT_DIR / f"shorts_{int(time.time())}.mp4"
        
        logger.info(f"Generating YouTube Short for prompt: {prompt}")
        
        # Step 1: Generate script from prompt
        script = self.script_generator.generate_script(prompt)
        
        # Step 2: Generate visual assets
        visual_assets = self._generate_visual_assets(script, style)
        if not visual_assets:
            logger.error("Failed to generate visual assets")
            return None
        
        # Step 3: Generate voiceover audio
        audio_path = self.audio_generator.generate_voiceover(script)
        if not audio_path:
            logger.error("Failed to generate voiceover")
            return None
        
        # Step 4: Generate captions
        captions = self.caption_generator.generate_captions(script, audio_path)
        
        # Step 5: Compose the final video
        output_path = self.video_composer.compose_video(
            visual_assets, audio_path, captions, output_path
        )
        
        if output_path:
            logger.info(f"Video generation complete: {output_path}")
        else:
            logger.error("Failed to compose final video")
        
        return output_path
    
    def _generate_visual_assets(self, script, style=None):
        """Generate visual assets for each part of the script"""
        style = style or self.config.get("default_style", "educational")
        style_config = self.config.get("visual_styles", {}).get(style, {})
        
        prompt_prefix = style_config.get("prompt_prefix", "")
        negative_prompt = style_config.get("negative_prompt", "")
        
        visual_assets = []
        
        # Generate hook visual
        hook_prompt = f"{prompt_prefix} {script['hook']}, vertical format for YouTube Shorts"
        hook_image_path = self.ai_provider.generate_image(
            hook_prompt, negative_prompt=negative_prompt
        )
        
        if hook_image_path:
            # Generate hook video
            hook_video_path = self.ai_provider.generate_video(
                hook_image_path,
                f"Smooth camera movement, {script['hook']}"
            )
            
            # If video generation failed, use the static image
            asset_path = hook_video_path or hook_image_path
            
            visual_assets.append({
                "path": asset_path,
                "text": script["hook"],
                "type": "ai_generated_video" if hook_video_path else "ai_generated_image",
                "duration": 3.0
            })
        
        # Generate visuals for each section
        for section in script["sections"]:
            section_prompt = f"{prompt_prefix} {section}, vertical format for YouTube Shorts"
            section_image_path = self.ai_provider.generate_image(
                section_prompt, negative_prompt=negative_prompt
            )
            
            if section_image_path:
                # Generate section video
                section_video_path = self.ai_provider.generate_video(
                    section_image_path,
                    f"Smooth camera movement, {section}"
                )
                
                # If video generation failed, use the static image
                asset_path = section_video_path or section_image_path
                
                visual_assets.append({
                    "path": asset_path,
                    "text": section,
                    "type": "ai_generated_video" if section_video_path else "ai_generated_image",
                    "duration": 8.0
                })
        
        # Generate CTA visual
        cta_prompt = f"{prompt_prefix} {script['cta']}, call to action, vertical format for YouTube Shorts"
        cta_image_path = self.ai_provider.generate_image(
            cta_prompt, negative_prompt=negative_prompt
        )
        
        if cta_image_path:
            # Generate CTA video
            cta_video_path = self.ai_provider.generate_video(
                cta_image_path,
                f"Energetic movement, {script['cta']}"
            )
            
            # If video generation failed, use the static image
            asset_path = cta_video_path or cta_image_path
            
            visual_assets.append({
                "path": asset_path,
                "text": script["cta"],
                "type": "ai_generated_video" if cta_video_path else "ai_generated_image",
                "duration": 3.0
            })
        
        return visual_assets

# ===============================
# Command Line Interface
# ===============================

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="AI Shorts Generator")
    parser.add_argument("--prompt", type=str, help="Text prompt for the video")
    parser.add_argument("--output", type=str, help="Output filename")
    parser.add_argument("--style", type=str, help="Visual style to use")
    parser.add_argument("--provider", type=str, help="AI provider to use")
    
    args = parser.parse_args()
    
    # Load config
    config_path = CONFIG_DIR / "config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        config = DEFAULT_CONFIG
    
    # Override config with command line arguments
    if args.provider:
        config["ai_provider"] = args.provider
    
    # Create the shorts generator
    generator = AIShortsGenerator(config)
    
    # Generate video from prompt
    if args.prompt:
        output_path = args.output if args.output else None
        style = args.style if args.style else None
        
        result = generator.generate_video_from_prompt(
            prompt=args.prompt,
            output_path=output_path,
            style=style
        )
        
        if result:
            print(f"\n✅ YouTube Short generated successfully!")
            print(f"📁 Output: {result}")
        else:
            print(f"\n❌ Failed to generate YouTube Short")
    else:
        # Interactive mode
        print("\n🎬 AI Shorts Generator Interactive Mode 🎬")
        prompt = input("Enter a prompt for your YouTube Short: ")
        
        if prompt:
            result = generator.generate_video_from_prompt(prompt)
            
            if result:
                print(f"\n✅ YouTube Short generated successfully!")
                print(f"📁 Output: {result}")
            else:
                print(f"\n❌ Failed to generate YouTube Short")

if __name__ == "__main__":
    main()#!/usr/bin/env python3