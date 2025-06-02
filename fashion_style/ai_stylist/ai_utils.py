from openai import OpenAI
import os
from django.conf import settings
import json
import base64

class FashionAI:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_outfit_suggestion(self, occasion, style_preference, weather=None, color_preference=None, additional_info=None):
        """Generate outfit suggestions based on user preferences"""
        
        prompt = f"""
        As a professional fashion stylist, suggest a complete outfit for the following requirements:
        
        Occasion: {occasion}
        Style Preference: {style_preference}
        """
        
        if weather:
            prompt += f"\nWeather: {weather}"
        if color_preference:
            prompt += f"\nColor Preference: {color_preference}"
        if additional_info:
            prompt += f"\nAdditional Information: {additional_info}"
        
        prompt += """
        
        Please provide:
        1. A detailed outfit description including specific clothing items
        2. Color combinations that work well
        3. Accessories recommendations
        4. Styling tips
        5. Where to shop for similar items (general suggestions)
        
        Make it practical and stylish. Format your response in a clear, organized manner.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional fashion stylist with expertise in creating stylish and practical outfit recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't generate an outfit suggestion at the moment. Error: {str(e)}"
    
    def analyze_fashion_image(self, image_path):
        """Analyze fashion image and provide styling suggestions"""
        
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this fashion image and provide detailed styling suggestions. Include color analysis, style assessment, and recommendations for improvement or complementary pieces."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't analyze the image. Error: {str(e)}"
    
    def chat_with_stylist(self, message, conversation_history=None):
        """General fashion chat functionality"""
        
        messages = [
            {"role": "system", "content": "You are a knowledgeable fashion stylist. Help users with fashion advice, styling tips, trends, and outfit suggestions. Be friendly, practical, and encouraging."}
        ]
        
        # Add conversation history if available
        if conversation_history:
            for conv in conversation_history[-5:]:  # Last 5 conversations for context
                messages.append({"role": "user", "content": conv.user_message})
                messages.append({"role": "assistant", "content": conv.ai_response})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't process your message. Error: {str(e)}"
    
    def update_user_profile(self, user, conversation_data, outfit_data):
        """Update user's conversation and outfit fields"""
        try:
            # Parse existing data or initialize empty
            current_conversations = json.loads(user.conversation) if user.conversation else []
            current_outfits = json.loads(user.outfits) if user.outfits else []
            
            # Add new conversation data
            if conversation_data:
                current_conversations.append({
                    'timestamp': conversation_data.created_at.isoformat(),
                    'message': conversation_data.user_message,
                    'response': conversation_data.ai_response
                })
            
            # Add new outfit data
            if outfit_data:
                current_outfits.append({
                    'timestamp': outfit_data.created_at.isoformat(),
                    'occasion': outfit_data.occasion,
                    'style': outfit_data.style_preference,
                    'description': outfit_data.outfit_description,
                    'is_favorite': outfit_data.is_favorite
                })
            
            # Keep only last 50 conversations and 20 outfits to manage size
            user.conversation = json.dumps(current_conversations[-50:])
            user.outfits = json.dumps(current_outfits[-20:])
            user.save()
            
        except Exception as e:
            print(f"Error updating user profile: {e}")