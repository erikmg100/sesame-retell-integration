#!/usr/bin/env python3
"""
Retell AI Bridge for SesameAI Integration
Connects SesameAI's voice technology with Retell AI agents
"""

import asyncio
import json
import logging
import os
import threading
import time
from typing import Dict, List, Optional
import websockets
from websockets.server import WebSocketServerProtocol
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

# Import SesameAI components
try:
    from sesame_ai import SesameAI, SesameWebSocket, TokenManager
    SESAME_AVAILABLE = True
except ImportError:
    print("SesameAI library not available. Install with: pip install -e .")
    SESAME_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="SesameAI + Retell Bridge", version="1.0.0")

class RetellSesameAgent:
    """
    Bridge between Retell AI and SesameAI voice technology
    """
    
    def __init__(self):
        self.sesame_client = None
        self.sesame_ws = None
        self.token_manager = None
        self.conversation_history: Dict[str, List] = {}
        self.active_calls: Dict[str, Dict] = {}
        
        # Initialize SesameAI if available
        if SESAME_AVAILABLE:
            self.initialize_sesame()
    
    def initialize_sesame(self):
        """Initialize SesameAI connection"""
        try:
            # Create SesameAI client
            self.sesame_client = SesameAI()
            
            # Initialize token manager
            token_file = os.getenv('SESAME_TOKEN_FILE', 'token.json')
            self.token_manager = TokenManager(
                self.sesame_client, 
                token_file=token_file
            )
            
            logger.info("SesameAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SesameAI: {e}")
            self.sesame_client = None
    
    def get_sesame_websocket(self, character="Maya"):
        """Get or create SesameAI WebSocket connection"""
        if not self.sesame_client or not self.token_manager:
            return None
            
        try:
            # Get valid token
            id_token = self.token_manager.get_valid_token()
            
            # Create WebSocket connection
            ws = SesameWebSocket(
                id_token=id_token,
                character=character,
                client_name="Retell-Bridge"
            )
            
            return ws
            
        except Exception as e:
            logger.error(f"Failed to create SesameAI WebSocket: {e}")
            return None
    
    def enhance_response_with_sesame(self, text: str, context: List = None) -> str:
        """
        Enhance text response with SesameAI voice presence principles
        """
        if not text:
            return text
            
        # Apply voice presence enhancements
        enhanced_text = self.add_conversational_flow(text)
        enhanced_text = self.add_emotional_intelligence(enhanced_text, context)
        enhanced_text = self.add_personality_consistency(enhanced_text)
        
        return enhanced_text
    
    def add_conversational_flow(self, text: str) -> str:
        """Add natural conversational flow markers"""
        # Add thoughtful pauses for more natural speech
        text = text.replace('. ', '... ')
        
        # Add natural fillers occasionally
        if len(text) > 100 and 'actually' not in text.lower():
            text = f"You know, {text}"
        
        return text
    
    def add_emotional_intelligence(self, text: str, context: List = None) -> str:
        """Add emotional intelligence based on conversation context"""
        if not context:
            return text
            
        # Analyze recent messages for emotional cues
        recent_messages = context[-3:] if len(context) >= 3 else context
        emotional_context = self.detect_emotional_context(recent_messages)
        
        if 'stress' in emotional_context:
            text = f"I can sense this might be stressful... {text} Take your time with this."
        elif 'excitement' in emotional_context:
            text = f"I love your enthusiasm! {text}"
        elif 'confusion' in emotional_context:
            text = f"Let me help clarify that. {text}"
            
        return text
    
    def detect_emotional_context(self, messages: List) -> List[str]:
        """Simple emotion detection from conversation context"""
        emotions = []
        
        for msg in messages:
            content = msg.get('content', '').lower()
            
            if any(word in content for word in ['stress', 'worried', 'anxious', 'overwhelmed']):
                emotions.append('stress')
            if any(word in content for word in ['excited', 'great', 'awesome', 'amazing']):
                emotions.append('excitement')
            if any(word in content for word in ['confused', 'understand', 'unclear', 'what']):
                emotions.append('confusion')
                
        return emotions
    
    def add_personality_consistency(self, text: str) -> str:
        """Maintain consistent personality traits"""
        # Ensure friendly, helpful tone
        if not any(greeting in text.lower() for greeting in ['hi', 'hello', 'hey']):
            if len(text) > 150:  # Longer responses get personality markers
                text = f"{text} I'm here to help you with whatever you need!"
                
        return text
    
    async def generate_response(self, messages: List[Dict], call_id: str) -> str:
        """Generate response using SesameAI if available, otherwise use enhanced text"""
        
        # Get conversation history for this call
        history = self.conversation_history.get(call_id, [])
        
        # If SesameAI is available, try to use it
        if SESAME_AVAILABLE and self.sesame_client:
            try:
                # For now, use text enhancement with SesameAI principles
                # In future versions, this could integrate with actual SesameAI voice generation
                last_message = messages[-1] if messages else {}
                user_text = last_message.get('content', '')
                
                # Generate contextual response
                response = self.generate_contextual_response(user_text, history)
                
                # Enhance with SesameAI voice presence
                enhanced_response = self.enhance_response_with_sesame(response, history)
                
                return enhanced_response
                
            except Exception as e:
                logger.error(f"Error generating SesameAI response: {e}")
                return self.fallback_response(messages)
        else:
            return self.fallback_response(messages)
    
    def generate_contextual_response(self, user_text: str, history: List) -> str:
        """Generate contextual response based on conversation history"""
        
        # Simple response generation based on user input
        user_lower = user_text.lower()
        
        if any(greeting in user_lower for greeting in ['hello', 'hi', 'hey']):
            return "Hello! I'm your AI assistant powered by SesameAI technology. How can I help you today?"
        
        if any(question in user_lower for question in ['how are you', 'how do you do']):
            return "I'm doing wonderfully, thank you for asking! I'm here and ready to assist you."
        
        if any(help_word in user_lower for help_word in ['help', 'assist', 'support']):
            return "I'd be happy to help you! What specifically can I assist you with?"
        
        if any(thanks in user_lower for thanks in ['thank', 'thanks']):
            return "You're very welcome! I'm glad I could help. Is there anything else I can do for you?"
        
        # Default conversational response
        return "That's interesting! Tell me more about that, I'm here to listen and help however I can."
    
    def fallback_response(self, messages: List[Dict]) -> str:
        """Fallback response when SesameAI is not available"""
        return "I'm here to help you. How can I assist you today?"


# Global agent instance
retell_sesame_agent = RetellSesameAgent()

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "SesameAI + Retell Bridge Running",
        "version": "1.0.0",
        "sesame_available": SESAME_AVAILABLE,
        "capabilities": [
            "Voice Presence Technology",
            "Emotional Intelligence", 
            "Conversational Dynamics",
            "Contextual Awareness"
        ]
    })

@app.websocket("/llm-websocket/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """
    Retell AI WebSocket endpoint with SesameAI enhancement
    """
    await websocket.accept()
    logger.info(f"New Retell session with SesameAI: {call_id}")
    
    # Initialize conversation for this call
    retell_sesame_agent.conversation_history[call_id] = []
    retell_sesame_agent.active_calls[call_id] = {
        "start_time": time.time(),
        "message_count": 0
    }
    
    # Send initial greeting
    greeting_response = {
        "response_id": 0,
        "content": "Hey there! I'm your AI assistant enhanced with SesameAI's voice presence technology. I'm here to have a genuine, natural conversation with you. How are you doing today?",
        "content_complete": True,
        "end_call": False
    }
    
    await websocket.send_text(json.dumps(greeting_response))
    
    try:
        while True:
            # Receive message from Retell
            data = await websocket.receive_text()
            
            try:
                request = json.loads(data)
                
                # Handle different interaction types
                interaction_type = request.get("interaction_type")
                
                if interaction_type == "update_only":
                    # Update conversation history
                    transcript = request.get("transcript", [])
                    if transcript:
                        last_message = transcript[-1]
                        history = retell_sesame_agent.conversation_history[call_id]
                        
                        # Add to history if not already there
                        if not history or history[-1].get('content') != last_message.get('content'):
                            history.append(last_message)
                            retell_sesame_agent.conversation_history[call_id] = history[-10:]  # Keep last 10
                    
                    continue
                
                elif interaction_type in ["response_required", "reminder_required"]:
                    # Generate response using SesameAI
                    transcript = request.get("transcript", [])
                    
                    if interaction_type == "reminder_required":
                        # Handle quiet moments
                        transcript.append({
                            "role": "user", 
                            "content": "(User has been quiet for a while)"
                        })
                    
                    # Generate enhanced response
                    response_content = await retell_sesame_agent.generate_response(
                        transcript, call_id
                    )
                    
                    # Update call statistics
                    retell_sesame_agent.active_calls[call_id]["message_count"] += 1
                    
                    # Send response back to Retell
                    response = {
                        "response_id": request.get("response_id"),
                        "content": response_content,
                        "content_complete": True,
                        "end_call": False
                    }
                    
                    await websocket.send_text(json.dumps(response))
                    logger.info(f"Sent SesameAI-enhanced response: {response_content[:100]}...")
                    
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON message")
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call: {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cleanup
        if call_id in retell_sesame_agent.conversation_history:
            del retell_sesame_agent.conversation_history[call_id]
        if call_id in retell_sesame_agent.active_calls:
            del retell_sesame_agent.active_calls[call_id]

@app.get("/stats")
async def get_stats():
    """Get current statistics"""
    return JSONResponse({
        "active_calls": len(retell_sesame_agent.active_calls),
        "sesame_available": SESAME_AVAILABLE,
        "call_details": retell_sesame_agent.active_calls
    })

if __name__ == "__main__":
    # Environment configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting SesameAI + Retell Bridge on {HOST}:{PORT}")
    logger.info(f"SesameAI Available: {SESAME_AVAILABLE}")
    
    # Run the server
    uvicorn.run(
        "retell_bridge:app",
        host=HOST,
        port=PORT,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20
    )
