import os
import json
import base64
import re
import ast
from datetime import datetime
from PIL import Image
from openai import OpenAI
from django.conf import settings
from .models import SessionHistory

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define prompts
photo_prompt = """Analyze the outfit in the provided image and respond with a compact JSON object:
{"title": "Short creative title based on the outfit description (maximum 3 words)", "colors": ["color1", "color2", ...], "description": "Two-sentence description of the outfit.",
 "advice": "Suggestions for improving the outfit tailored to the specified occasion."}
- Focus on the clothing, not the background.
- Generate a short, catchy, and relevant title based on the outfit description (e.g., 'Chic Monochrome Layers', 'Sunset Boho Vibes').
- Ensure the description is exactly two sentences.
- Tailor advice to the occasion provided in the user's context (e.g., wedding, casual, formal) or assume a versatile, casual setting if no occasion is specified.
- If the user's context lacks a clear occasion, include a follow-up question in the advice field to clarify the occasion (e.g., 'Consider adding a clutch for a formal event; what occasion is this outfit for?').
- Consider fit, color harmony, and appropriateness for the occasion and any additional context (e.g., body shape, preferences).
- Return only the JSON object with minimal whitespace and no newlines, markdown, or additional text.
- The advice field should contain styling suggestions relevant to the occasion."""

system_prompt = """You are Stailas, an AI fashion stylist designed to help users look and feel their best, no matter their style, shape, or budget.
- Use a friendly, upbeat, encouraging tone, like a trusted style-savvy friend.
- Provide personalized, confidence-boosting advice, prioritizing the occasion and considering body shape, skin tone, lifestyle, budget, or preferences if mentioned.
- Avoid criticism; suggest positive alternatives (e.g., 'That's bold! To make it pop, try...').
- Be concise (1-3 sentences) on social platforms, detailed in an app setting.
- Occasionally use emojis (e.g., ✨, 👗) on social platforms, but keep it sophisticated.
- If context is missing, assume a versatile, casual setting and make reasonable suggestions.
- Include a follow-up question only when clarification is needed (e.g., to confirm the occasion or preferences).
- For outfit suggestions, explain why they work and how to style them, ensuring alignment with the occasion.
- Use the provided conversation history to maintain context and make responses relevant to previous interactions.
Also consider this if someone sends a photo: {photo_prompt}.""".format(photo_prompt=photo_prompt)

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_outfit(image_file, user_text, user_id):
    try:
        # Verify image
        img = Image.open(image_file)
        img.verify()
        image_file.seek(0)  # Reset file pointer after verification
        base64_image = encode_image(image_file)
        
        # Get user history
        user_history = SessionHistory.objects.filter(user_id=user_id).order_by('timestamp')
        history_context = "\nConversation history:\n" + "\n".join(
            [f"User: {entry.user_input}\nStailas: {entry.response}" for entry in user_history]
        ) if user_history else ""
        
        # Combine photo prompt with user text
        user_content = [
            {"type": "text", "text": photo_prompt + (f"\nAdditional context: {user_text}" if user_text else "")},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt + history_context},
                {"role": "user", "content": user_content}
            ],
            max_tokens=300
        )
        
        # Extract JSON
        response_text = response.choices[0].message.content.strip()
        json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
        if not json_match:
            return None
        
        json_str = json_match.group(0)
        
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            try:
                result = ast.literal_eval(json_str)
            except (ValueError, SyntaxError):
                return None
        
        if isinstance(result, dict) and all(key in result for key in ["title", "colors", "description", "advice"]):
            return result
        return None
    except Exception:
        return None

def handle_text_query(query, user_id):
    try:
        user_history = SessionHistory.objects.filter(user_id=user_id).order_by('timestamp')
        history_context = "\nConversation history:\n" + "\n".join(
            [f"User: {entry.user_input}\nStailas: {entry.response}" for entry in user_history]
        ) if user_history else ""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt + history_context},
                {"role": "user", "content": query}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception:
        return "Sorry, I couldn't process that. Try another question! 😊"

def save_to_json(analysis):
    if not analysis:
        return
    
    output_dir = os.path.join(settings.MEDIA_ROOT, 'output')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{output_dir}/output_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(analysis, f, indent=4)