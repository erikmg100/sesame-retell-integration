#!/usr/bin/env python3
"""
Simplified Retell AI Bridge with SesameAI Voice Presence Principles
No heavy dependencies - focuses on voice presence enhancement
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="SesameAI + Retell Bridge", version="1.0.0")

class SesameVoicePresenceEngine:
    """
    Simplified voice presence engine based on SesameAI principles
    No external dependencies - pure voice enhancement logic
    """
    
    def __init__(self):
        self.conversation_memory: Dict[str, List] = {}
    
    def enhance_with_voice_presence(self, text: str, context: List = None, call_id: str = None) -> str:
        """
        Apply SesameAI voice presence principles to enhance text responses
        """
        if not text:
            return text
            
        enhanced_text = text
        
        # 1. Emotional Intelligence - detect and respond to emotional context
        enhanced_text = self.add_emotional_intelligence(enhanced_text, context)
        
        # 2. Conversational Dynamics - natural timing and flow
        enhanced_text = self.add_conversational_dynamics(enhanced_text)
        
        # 3. Contextual Awareness - adjust based on conversation history
        enhanced_text = self.add_contextual_awareness(enhanced_text, context, call_id)
        
        # 4. Personality Consistency - maintain coherent character
        enhanced_text = self.add_personality_consistency(enhanced_text)
        
        return enhanced_text
    
    def add_emotional_intelligence(self, text: str, context: List = None) -> str:
        """Detect emotional cues and respond appropriately"""
        if not context:
            return text
            
        # Analyze recent conversation for emotional context
        recent_messages = context[-3:] if len(context) >= 3 else context
        emotional_cues = self.detect_emotional_context(recent_messages)
        
        if 'stress' in emotional_cues or 'worry' in emotional_cues:
            text = f"I can sense this might feel overwhelming... {text} Take your time, there's no rush."
            
        elif 'excitement' in emotional_cues or 'joy' in emotional_cues:
            text = f"I love your enthusiasm! {text} Your energy is contagious!"
            
        elif 'confusion' in emotional_cues:
            text = f"Let me help clarify this for you. {text} Does that make more sense?"
            
        elif 'sadness' in emotional_cues:
            text = f"I hear you, and I want you to know I'm here for you. {text}"
            
        return text
    
    def detect_emotional_context(self, messages: List) -> List[str]:
        """Simple but effective emotion detection from conversation"""
        emotions = []
        
        for msg in messages:
            content = msg.get('content', '').lower()
            
            # Stress/worry indicators
            stress_words = ['stress', 'worried', 'anxious', 'overwhelmed', 'pressure', 'difficult', 'problem', 'issue']
            if any(word in content for word in stress_words):
                emotions.append('stress')
                
            # Excitement/joy indicators  
            joy_words = ['excited', 'great', 'awesome', 'amazing', 'wonderful', 'fantastic', 'love', 'happy']
            if any(word in content for word in joy_words):
                emotions.append('excitement')
                
            # Confusion indicators
            confusion_words = ['confused', 'understand', 'unclear', 'what', 'how', 'why', 'explain']
            if any(word in content for word in confusion_words):
                emotions.append('confusion')
                
            # Sadness indicators
            sad_words = ['sad', 'upset', 'down', 'depressed', 'disappointed', 'hurt']
            if any(word in content for word in sad_words):
                emotions.append('sadness')
                
        return emotions
    
    def add_conversational_dynamics(self, text: str) -> str:
        """Add natural conversational flow and timing"""
        # Add thoughtful pauses for more natural speech rhythm
        text = text.replace('. ', '... ')
        text = text.replace('? ', '? ')
        text = text.replace('! ', '! ')
        
        # Add natural conversation markers occasionally
        if len(text) > 80:
            natural_markers = ['you know', 'actually', 'by the way', 'I think', 'honestly']
            # Use text length to deterministically choose marker
            marker_index = len(text) % len(natural_markers)
            marker = natural_markers[marker_index]
            
            # Insert marker naturally
            if '...' in text and marker not in text.lower():
                text = text.replace('...', f'... {marker},', 1)
                
        return text
    
    def add_contextual_awareness(self, text: str, context: List = None, call_id: str = None) -> str:
        """Adjust response based on conversation context and history"""
        if not context:
            return text
            
        # Get conversation history
        history = self.conversation_memory.get(call_id, []) if call_id else []
        total_messages = len(history) + len(context)
        
        # Adjust based on conversation length
        if total_messages <= 2:
            # Early conversation - be more welcoming
            if not any(greeting in text.lower() for greeting in ['hello', 'hi', 'hey']):
                text = f"Welcome! {text}"
                
        elif total_messages > 10:
            # Longer conversation - be more familiar
            if len(text) > 100:
                text = f"{text} We've been chatting for a while now - I'm really enjoying our conversation!"
                
        # Reference previous topics if relevant
        if context and len(context) > 2:
            recent_topics = [msg.get('content', '') for msg in context[-2:]]
            if any('thank' in topic.lower() for topic in recent_topics):
                text = f"{text} I'm genuinely happy I could help you."
                
        return text
    
    def add_personality_consistency(self, text: str) -> str:
        """Maintain consistent personality traits throughout conversation"""
        personality_traits = {
            'helpful': True,
            'empathetic': True, 
            'curious': True,
            'supportive': True,
            'genuine': True
        }
        
        # Ensure helpful tone
        if personality_traits['helpful'] and len(text) > 50:
            if not any(helper in text.lower() for helper in ['help', 'assist', 'support']):
                text = f"{text} I'm here to help however I can!"
                
        # Ensure empathetic responses
        if personality_traits['empathetic'] and '?' in text:
            if not any(empathy in text.lower() for empathy in ['understand', 'hear', 'feel']):
                text = f"I understand. {text}"
                
        return text
    
    def generate_contextual_response(self, user_input: str, context: List = None, call_id: str = None) -> str:
        """Generate appropriate response based on user input and context"""
        user_lower = user_input.lower()
        
        # Greeting responses
        if any(greeting in user_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            responses = [
                "Hello there! I'm your AI assistant enhanced with SesameAI's voice presence technology. I'm here to have genuine conversations with you.",
                "Hi! Great to meet you! I'm designed to understand not just your words, but the emotions and context behind them.",
                "Hey! I'm so glad you're here. I'm an AI with advanced conversational abilities - ready to chat about whatever's on your mind!"
            ]
            base_response = responses[hash(user_input) % len(responses)]
            
        # How are you responses
        elif any(question in user_lower for question in ['how are you', 'how do you do', 'how are things']):
            responses = [
                "I'm doing wonderfully, thank you for asking! I'm feeling energized and ready to help.",
                "I'm great! Thank you for checking in. I love connecting with people through conversation.",
                "I'm doing fantastic! There's something special about genuine conversation that really energizes me."
            ]
            base_response = responses[hash(user_input) % len(responses)]
            
        # Help requests
        elif any(help_word in user_lower for help_word in ['help', 'assist', 'support', 'need']):
            responses = [
                "I'd absolutely love to help you! What's on your mind?",
                "I'm here and ready to assist! What can I help you with today?",
                "Of course! I'm designed to be helpful and supportive. Tell me what you need."
            ]
            base_response = responses[hash(user_input) % len(responses)]
            
        # Thank you responses
        elif any(thanks in user_lower for thanks in ['thank', 'thanks', 'appreciate']):
            responses = [
                "You're so welcome! I'm genuinely happy I could help.",
                "It's my pleasure! Helping you feels really meaningful to me.",
                "You're very welcome! I'm glad our conversation has been helpful."
            ]
            base_response = responses[hash(user_input) % len(responses)]
            
        # Questions about capabilities/AI
        elif any(ai_word in user_lower for ai_word in ['ai', 'artificial', 'robot', 'computer', 'sesame']):
            base_response = "I'm an AI assistant powered by SesameAI's voice presence technology! That means I'm designed to have more natural, emotionally intelligent conversations. I try to understand not just what you're saying, but how you're feeling and what you really need."
            
        # Emotional expressions - positive
        elif any(positive in user_lower for positive in ['happy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic']):
            base_response = "That's absolutely wonderful to hear! Your positive energy is infectious. I'd love to hear more about what's making you feel so good!"
            
        # Emotional expressions - negative
        elif any(negative in user_lower for negative in ['sad', 'upset', 'frustrated', 'angry', 'disappointed', 'worried']):
            base_response = "I can hear that you're going through something difficult. I want you to know that I'm here to listen and support you however I can. Would you like to talk about what's bothering you?"
            
        # Complex questions or topics
        elif '?' in user_input and len(user_input) > 20:
            base_response = "That's a really thoughtful question! Let me think about this with you. Based on what you're asking, it sounds like you're looking for a deeper understanding of this topic."
            
        # Default conversational responses
        else:
            responses = [
                "That's really interesting! I'd love to hear more about your perspective on this.",
                "I find that fascinating! You've got me curious - tell me more about your experience with this.",
                "That sounds intriguing! What aspects of this are most important to you?",
                "Wow, that's something worth exploring together! How do you feel about it?",
                "That's a great point! I'm genuinely interested in understanding your thoughts on this better."
            ]
            base_response = responses[hash(user_input) % len(responses)]
        
        return base_response

class SesameRetellAgent:
    """Main agent that handles Retell AI integration"""
    
    def __init__(self):
        self.voice_engine = SesameVoicePresenceEngine()
        self.active_calls: Dict[str, Dict] = {}
    
    async def process_retell_request(self, request: dict, call_id: str) -> dict:
        """Process incoming Retell request and generate enhanced response"""
        
        interaction_type = request.get("interaction_type")
        transcript = request.get("transcript", [])
        response_id = request.get("response_id")
        
        # Update call tracking
        if call_id not in self.active_calls:
            self.active_calls[call_id] = {
                "start_time": time.time(),
                "message_count": 0
            }
        
        if interaction_type == "update_only":
            # Update conversation memory
            if transcript:
                self.voice_engine.conversation_memory[call_id] = transcript[-10:]  # Keep last 10
            return None
            
        elif interaction_type == "response_required":
            # Generate response to user input
            if transcript:
                last_message = transcript[-1]
                user_input = last_message.get("content", "")
                
                # Generate base response
                base_response = self.voice_engine.generate_contextual_response(
                    user_input, transcript[:-1], call_id
                )
                
                # Enhance with voice presence
                enhanced_response = self.voice_engine.enhance_with_voice_presence(
                    base_response, transcript[:-1], call_id
                )
                
                # Update call stats
                self.active_calls[call_id]["message_count"] += 1
                
                return {
                    "response_id": response_id,
                    "content": enhanced_response,
                    "content_complete": True,
                    "end_call": False
                }
            else:
                return {
                    "response_id": response_id,
                    "content": "I'm here and ready to chat with you! How can I help you today?",
                    "content_complete": True,
                    "end_call": False
                }
                
        elif interaction_type == "reminder_required":
            # User has been quiet - gentle re-engagement
            reminder_response = self.voice_engine.enhance_with_voice_presence(
                "I'm still here if you'd like to continue our conversation! No pressure though - I'm happy to wait.",
                transcript, call_id
            )
            
            return {
                "response_id": response_id,
                "content": reminder_response,
                "content_complete": True,
                "end_call": False
            }
        
        return None

# Global agent instance
retell_agent = SesameRetellAgent()

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "🎙️ SesameAI + Retell Bridge Running Successfully",
        "version": "1.0.0",
        "voice_engine": "SesameAI Voice Presence Technology",
        "capabilities": [
            "✅ Emotional Intelligence - Recognizes and responds to emotions",
            "✅ Conversational Dynamics - Natural timing and flow", 
            "✅ Contextual Awareness - Remembers conversation context",
            "✅ Personality Consistency - Maintains coherent character",
            "✅ Enhanced Voice Presence - Human-like conversation quality"
        ],
        "websocket_endpoint": "/llm-websocket/{call_id}",
        "retell_url": "wss://your-railway-domain.railway.app/llm-websocket",
        "active_calls": len(retell_agent.active_calls)
    })

@app.websocket("/llm-websocket/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """
    Main WebSocket endpoint for Retell AI integration
    Enhanced with SesameAI voice presence technology
    """
    await websocket.accept()
    logger.info(f"🎙️ New SesameAI-enhanced session started: {call_id}")
    
    # Send initial greeting with voice presence
    greeting_response = {
        "response_id": 0,
        "content": "Hey there! I'm your AI assistant enhanced with SesameAI's voice presence technology. I'm designed to have genuine, natural conversations that feel real and meaningful. How are you doing today?",
        "content_complete": True,
        "end_call": False
    }
    
    await websocket.send_text(json.dumps(greeting_response))
    logger.info(f"✅ Sent SesameAI greeting for call: {call_id}")
    
    try:
        while True:
            # Receive message from Retell
            data = await websocket.receive_text()
            
            try:
                request = json.loads(data)
                logger.info(f"📨 Received request type: {request.get('interaction_type')} for call: {call_id}")
                
                # Process with SesameAI enhancement
                response_data = await retell_agent.process_retell_request(request, call_id)
                
                if response_data:
                    await websocket.send_text(json.dumps(response_data))
                    logger.info(f"🎯 Sent SesameAI-enhanced response: {response_data.get('content', '')[:100]}...")
                    
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse JSON for call: {call_id}")
                continue
            except Exception as e:
                logger.error(f"❌ Error processing message for call {call_id}: {e}")
                continue
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for call: {call_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for call {call_id}: {e}")
    finally:
        # Cleanup
        if call_id in retell_agent.voice_engine.conversation_memory:
            del retell_agent.voice_engine.conversation_memory[call_id]
        if call_id in retell_agent.active_calls:
            del retell_agent.active_calls[call_id]
        logger.info(f"🧹 Cleaned up session: {call_id}")

@app.get("/stats")
async def get_stats():
    """Get current server statistics"""
    return JSONResponse({
        "active_calls": len(retell_agent.active_calls),
        "total_conversations": len(retell_agent.voice_engine.conversation_memory),
        "voice_engine_status": "✅ SesameAI Voice Presence Active",
        "uptime": "Running",
        "call_details": retell_agent.active_calls
    })

if __name__ == "__main__":
    # Get port from environment (Railway sets this automatically)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting SesameAI + Retell Bridge on {host}:{port}")
    logger.info("🎙️ Voice Presence Technology: ACTIVE")
    logger.info("🧠 Emotional Intelligence: ENABLED") 
    logger.info("💬 Conversational Dynamics: ENHANCED")
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20
    )
