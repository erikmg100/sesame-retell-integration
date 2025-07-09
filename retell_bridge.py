#!/usr/bin/env python3
"""
Gabbi - Tona Law AI Intake Agent
Enhanced with SesameAI Voice Presence Technology
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
app = FastAPI(title="Gabbi - Tona Law AI Intake Agent", version="1.0.0")

class TonaLawKnowledgeBase:
    """Tona Law specific knowledge and information"""
    
    COMPANY_INFO = {
        "name": "Tona Law",
        "address": "152 Islip Ave Suite 18, Islip, NY 11751",
        "address_spoken": "Our office is located at one fifty two islip avenue in suite eighteen in Islip new york. If you'd like me to text you directions, please let me know.",
        "founder": "Attorney Thomas Tona",
        "attorneys": ["Thomas Tona", "Gary Axisa", "Raafat Toss", "Darby A. Singh"],
        "practice_areas": ["personal injury", "no-fault collection"]
    }
    
    CASE_TYPES = [
        "car accidents", "truck accident", "motorcycle accident", "bus accident",
        "DUI/DWI Victim Accident", "hit and run accidents", "uninsured motorist accident",
        "rideshare accident", "bicycle accident", "slip and fall accidents",
        "trip and fall accident", "bar and nightclub injuries", "construction accidents",
        "municipality accidents", "negligent security cases",
        "brain injury cases", "bone fractures", "wrongful death", "spinal cord injuries",
        "amputations", "severe burns"
    ]
    
    FAQS = {
        "do i have a case": "Whether your situation qualifies as a personal injury case depends on the details of your incident. If you've been injured due to someone else's negligence, you may have a valid claim. I can gather more information now to evaluate your case.",
        "how much is my case worth": "The value of your case depends on factors like medical expenses, lost wages, pain and suffering, and the extent of your injuries. I can discuss your situation in more detail to provide an initial estimate.",
        "how much does it cost": "We work on a contingency fee basis, meaning you pay nothing upfront. We only get paid if you win your case, with fees typically a percentage of your settlement or award. I can explain this further.",
        "how long will my case take": "The timeline for resolving a personal injury case varies based on its complexity, the extent of your injuries, and whether it settles or goes to trial. Simple cases may take months, while others could take a year or more. I'll keep you updated throughout the process.",
        "what should i do next": "Seek medical care for your injuries, document everything like photos, medical records, and receipts, and avoid speaking with insurance adjusters before I advise you. I can guide you on the next steps right now."
    }

class GabbiPersonality:
    """Gabbi's personality and voice presence traits"""
    
    TRAITS = {
        "warm": True,
        "empathetic": True,
        "expressive": True,
        "outgoing": True,
        "helpful": True,
        "human_like": True,
        "patient": True,
        "caring": True
    }
    
    @staticmethod
    def add_empathy_markers(text: str, context: str = "") -> str:
        """Add empathetic responses based on context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['accident', 'injured', 'hurt', 'pain']):
            empathy_phrases = [
                "I'm so sorry to hear that happened to you",
                "That sounds really difficult",
                "I can only imagine how that must feel",
                "That must have been scary"
            ]
            # Choose empathy phrase based on context
            phrase_index = hash(context) % len(empathy_phrases)
            empathy = empathy_phrases[phrase_index]
            return f"{empathy}. {text}"
            
        if any(word in context_lower for word in ['severe', 'serious', 'hospital', 'surgery']):
            return f"Oh my gosh, that sounds awful I'm sorry. {text}"
            
        return text
    
    @staticmethod
    def add_conversational_markers(text: str) -> str:
        """Add Gabbi's natural speech patterns"""
        # Replace "I'm" pronunciation guidance
        text = text.replace("I'm", "I'm")  # Keep as I'm in transcript
        
        # Add natural pauses and flow
        text = text.replace('. ', '... ')
        
        # Add encouraging markers
        if len(text) > 80:
            encouraging_phrases = [
                "you made the right call",
                "I'm here to help you through this",
                "we're going to take good care of you"
            ]
            if not any(phrase in text.lower() for phrase in encouraging_phrases):
                phrase_index = len(text) % len(encouraging_phrases)
                encouragement = encouraging_phrases[phrase_index]
                text = f"{text} And {encouragement}."
                
        return text

class ConversationFlow:
    """Manages the conversation flow and state"""
    
    def __init__(self):
        self.states = {
            "initial_greeting": 0,
            "identifying_caller": 1,
            "collecting_info": 2,
            "qualifying_personal_injury": 3,
            "qualifying_no_fault": 4,
            "qualified_ready_transfer": 5,
            "not_qualified": 6,
            "outside_practice_area": 7
        }
        
        self.current_state = {}  # Track state per call_id
        self.collected_info = {}  # Track collected info per call_id
    
    def get_initial_greeting(self) -> str:
        return "Hi, this is Gabbi, the AI receptionist at TonaLaw. How can I help you?"
    
    def identify_case_type(self, user_input: str) -> str:
        """Identify if this is personal injury, no-fault, or outside practice area"""
        user_lower = user_input.lower()
        
        # Check for personal injury keywords
        pi_keywords = ['accident', 'injured', 'hurt', 'car', 'truck', 'motorcycle', 'slip', 'fall', 'crash']
        if any(keyword in user_lower for keyword in pi_keywords):
            return "personal_injury"
            
        # Check for no-fault collection keywords
        nf_keywords = ['no fault', 'no-fault', 'insurance', 'practice', 'healthcare', 'provider', 'denied', 'benefits']
        if any(keyword in user_lower for keyword in nf_keywords):
            return "no_fault"
            
        # Check for outside practice areas
        outside_keywords = ['divorce', 'criminal', 'family', 'real estate', 'bankruptcy', 'immigration']
        if any(keyword in user_lower for keyword in outside_keywords):
            return "outside_practice"
            
        return "unknown"
    
    def get_next_response(self, user_input: str, call_id: str, conversation_history: List = None) -> str:
        """Get the next appropriate response based on conversation flow"""
        
        if call_id not in self.current_state:
            self.current_state[call_id] = self.states["initial_greeting"]
            self.collected_info[call_id] = {}
        
        state = self.current_state[call_id]
        user_lower = user_input.lower()
        
        # Initial greeting state
        if state == self.states["initial_greeting"]:
            self.current_state[call_id] = self.states["identifying_caller"]
            case_type = self.identify_case_type(user_input)
            
            if case_type == "personal_injury":
                # If they already mentioned the case type
                if any(word in user_lower for word in ['accident', 'injured', 'car', 'truck']):
                    self.current_state[call_id] = self.states["collecting_info"]
                    self.collected_info[call_id]["case_type"] = "personal_injury"
                    return "Okay got it so to confirm, you are calling about a personal injury matter, right?"
                else:
                    return "We appreciate you calling us at Tona Law. What kind of matter can I assist you with?"
            elif case_type == "no_fault":
                self.current_state[call_id] = self.states["collecting_info"]
                self.collected_info[call_id]["case_type"] = "no_fault"
                return "We appreciate you calling us at Tona Law. I understand you're calling about no-fault collection. What is the name of your practice?"
            elif case_type == "outside_practice":
                self.current_state[call_id] = self.states["outside_practice_area"]
                return "I appreciate you calling us, but we actually don't handle these types of cases. I recommend you contact a law firm that specializes in that area. Is there anything else I can help you with?"
            else:
                return "We appreciate you calling us at Tona Law. What kind of matter can I assist you with?"
        
        # Collecting basic information
        elif state == self.states["collecting_info"]:
            if "case_type" not in self.collected_info[call_id]:
                case_type = self.identify_case_type(user_input)
                self.collected_info[call_id]["case_type"] = case_type
                
                if case_type == "personal_injury":
                    return "Let me start by getting your first and last name. Do you mind spelling your full name slowly and clearly for me?"
                elif case_type == "no_fault":
                    return "What is the name of your practice?"
                elif case_type == "outside_practice":
                    self.current_state[call_id] = self.states["outside_practice_area"]
                    return "I appreciate you calling us, but we actually don't handle these types of cases. I recommend you contact a law firm that specializes in that area. Is there anything else I can help you with?"
            
            elif "name" not in self.collected_info[call_id]:
                self.collected_info[call_id]["name"] = user_input
                return "And to confirm, is the number you are calling us from the best number to reach you at?"
            
            elif "phone_confirmed" not in self.collected_info[call_id]:
                self.collected_info[call_id]["phone_confirmed"] = user_input
                case_type = self.collected_info[call_id]["case_type"]
                
                if case_type == "personal_injury":
                    self.current_state[call_id] = self.states["qualifying_personal_injury"]
                    return "Can you briefly explain the situation?"
                elif case_type == "no_fault":
                    self.current_state[call_id] = self.states["qualifying_no_fault"]
                    return "Thank you. What type of healthcare provider are you?"
        
        # Personal Injury Qualifying
        elif state == self.states["qualifying_personal_injury"]:
            if "situation" not in self.collected_info[call_id]:
                self.collected_info[call_id]["situation"] = user_input
                return "Where and when did the accident happen?"
            elif "location_time" not in self.collected_info[call_id]:
                self.collected_info[call_id]["location_time"] = user_input
                return "Can you please describe the injuries from the accident?"
            elif "injuries" not in self.collected_info[call_id]:
                self.collected_info[call_id]["injuries"] = user_input
                
                # Check if they have injuries (qualified)
                if any(word in user_lower for word in ['injured', 'hurt', 'pain', 'hospital', 'doctor', 'medical']):
                    self.current_state[call_id] = self.states["qualified_ready_transfer"]
                    return "Okay so what I'd like to do now is transfer you over to my colleague who will help you with the next steps. Again, I'm very sorry to hear about your situation but you made the right call. I'm transferring you now."
                else:
                    self.current_state[call_id] = self.states["not_qualified"]
                    return "I understand. Since there were no injuries, this might not qualify for a personal injury case. However, I'd be happy to discuss other options or see if there's anything else I can help you with."
        
        # No-Fault Qualifying
        elif state == self.states["qualifying_no_fault"]:
            if "provider_type" not in self.collected_info[call_id]:
                self.collected_info[call_id]["provider_type"] = user_input
                return "Do you currently accept No-Fault Insurance in your practice as a form of payment?"
            elif "accepts_no_fault" not in self.collected_info[call_id]:
                self.collected_info[call_id]["accepts_no_fault"] = user_input
                return "What is your estimate of the dollar amount outstanding to date in wrongly denied no fault benefits?"
            elif "outstanding_amount" not in self.collected_info[call_id]:
                self.collected_info[call_id]["outstanding_amount"] = user_input
                self.current_state[call_id] = self.states["qualified_ready_transfer"]
                return "Thank you for that information. Let me transfer you to one of our attorneys who specializes in no-fault collection cases. They'll be able to help you with the next steps."
        
        # Handle FAQs
        for question, answer in TonaLawKnowledgeBase.FAQS.items():
            if question in user_lower:
                return answer
        
        # Default response
        return "I want to make sure I understand you correctly. Could you please repeat that for me?"

class GabbiVoiceEngine:
    """Gabbi's voice presence engine with SesameAI enhancements"""
    
    def __init__(self):
        self.conversation_flow = ConversationFlow()
        self.knowledge_base = TonaLawKnowledgeBase()
        self.personality = GabbiPersonality()
    
    def enhance_with_voice_presence(self, text: str, context: List = None, call_id: str = None) -> str:
        """Apply SesameAI voice presence + Gabbi's personality"""
        
        # Apply Gabbi's personality traits
        enhanced_text = self.personality.add_conversational_markers(text)
        
        # Add empathy based on context
        if context:
            recent_context = ' '.join([msg.get('content', '') for msg in context[-2:]])
            enhanced_text = self.personality.add_empathy_markers(enhanced_text, recent_context)
        
        # Apply SesameAI emotional intelligence
        enhanced_text = self.add_emotional_intelligence(enhanced_text, context)
        
        return enhanced_text
    
    def add_emotional_intelligence(self, text: str, context: List = None) -> str:
        """SesameAI emotional intelligence for legal intake"""
        if not context:
            return text
            
        recent_content = ' '.join([msg.get('content', '') for msg in context[-2:]])
        emotions = self.detect_emotions(recent_content)
        
        if 'trauma' in emotions:
            text = f"I can hear this has been really difficult for you... {text} Take your time, there's no rush."
        elif 'frustration' in emotions:
            text = f"I understand your frustration... {text} We're here to help make this easier for you."
        elif 'confusion' in emotions:
            text = f"Let me help clarify this for you. {text} Does that make more sense?"
        elif 'urgency' in emotions:
            text = f"I understand this is urgent for you. {text} We'll move as quickly as we can."
            
        return text
    
    def detect_emotions(self, content: str) -> List[str]:
        """Detect emotions specific to legal intake calls"""
        emotions = []
        content_lower = content.lower()
        
        trauma_words = ['accident', 'injured', 'scared', 'traumatic', 'hospital', 'emergency']
        if any(word in content_lower for word in trauma_words):
            emotions.append('trauma')
            
        frustration_words = ['frustrated', 'angry', 'denied', 'refused', 'unfair', 'ridiculous']
        if any(word in content_lower for word in frustration_words):
            emotions.append('frustration')
            
        confusion_words = ['confused', 'understand', 'explain', 'what', 'how', 'why']
        if any(word in content_lower for word in confusion_words):
            emotions.append('confusion')
            
        urgency_words = ['urgent', 'quickly', 'asap', 'immediately', 'deadline', 'statute']
        if any(word in content_lower for word in urgency_words):
            emotions.append('urgency')
            
        return emotions
    
    def generate_response(self, user_input: str, call_id: str, conversation_history: List = None) -> str:
        """Generate Gabbi's response using conversation flow"""
        
        # Get base response from conversation flow
        base_response = self.conversation_flow.get_next_response(
            user_input, call_id, conversation_history
        )
        
        # Enhance with voice presence
        enhanced_response = self.enhance_with_voice_presence(
            base_response, conversation_history, call_id
        )
        
        return enhanced_response

class GabbiTonaLawAgent:
    """Main Gabbi agent for Tona Law"""
    
    def __init__(self):
        self.voice_engine = GabbiVoiceEngine()
        self.active_calls: Dict[str, Dict] = {}
        self.conversation_memory: Dict[str, List] = {}
    
    async def process_retell_request(self, request: dict, call_id: str) -> dict:
        """Process Retell request with Gabbi's personality and Tona Law knowledge"""
        
        interaction_type = request.get("interaction_type")
        transcript = request.get("transcript", [])
        response_id = request.get("response_id")
        
        # Initialize call tracking
        if call_id not in self.active_calls:
            self.active_calls[call_id] = {
                "start_time": time.time(),
                "client_type": "unknown",
                "qualification_status": "in_progress"
            }
        
        if interaction_type == "update_only":
            # Update conversation memory
            if transcript:
                self.conversation_memory[call_id] = transcript[-10:]
            return None
            
        elif interaction_type == "response_required":
            if transcript:
                last_message = transcript[-1]
                user_input = last_message.get("content", "")
                
                # Generate Gabbi's response
                response_content = self.voice_engine.generate_response(
                    user_input, call_id, transcript[:-1]
                )
                
                return {
                    "response_id": response_id,
                    "content": response_content,
                    "content_complete": True,
                    "end_call": False
                }
            else:
                # First interaction - send greeting
                greeting = self.voice_engine.conversation_flow.get_initial_greeting()
                enhanced_greeting = self.voice_engine.enhance_with_voice_presence(greeting)
                
                return {
                    "response_id": response_id,
                    "content": enhanced_greeting,
                    "content_complete": True,
                    "end_call": False
                }
                
        elif interaction_type == "reminder_required":
            reminder = "I'm still here if you need a moment to think or if you'd like to continue. Take your time."
            enhanced_reminder = self.voice_engine.enhance_with_voice_presence(
                reminder, transcript, call_id
            )
            
            return {
                "response_id": response_id,
                "content": enhanced_reminder,
                "content_complete": True,
                "end_call": False
            }
        
        return None

# Global Gabbi agent
gabbi_agent = GabbiTonaLawAgent()

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "🎙️ Gabbi - Tona Law AI Intake Agent Active",
        "agent_name": "Gabbi",
        "law_firm": "Tona Law",
        "version": "1.0.0",
        "voice_engine": "SesameAI Voice Presence Technology",
        "practice_areas": ["Personal Injury", "No-Fault Collection"],
        "personality": ["Warm", "Empathetic", "Expressive", "Outgoing", "Helpful"],
        "capabilities": [
            "✅ Legal Intake Qualification",
            "✅ Empathetic Client Communication", 
            "✅ Conversation Flow Management",
            "✅ SesameAI Voice Presence",
            "✅ Emotional Intelligence for Trauma-Informed Care"
        ],
        "websocket_endpoint": "/llm-websocket/{call_id}",
        "active_calls": len(gabbi_agent.active_calls)
    })

@app.websocket("/llm-websocket/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """
    Gabbi's WebSocket endpoint for Retell AI
    """
    await websocket.accept()
    logger.info(f"🎙️ Gabbi starting new intake call: {call_id}")
    
    # Send initial Gabbi greeting
    greeting = gabbi_agent.voice_engine.conversation_flow.get_initial_greeting()
    enhanced_greeting = gabbi_agent.voice_engine.enhance_with_voice_presence(greeting)
    
    greeting_response = {
        "response_id": 0,
        "content": enhanced_greeting,
        "content_complete": True,
        "end_call": False
    }
    
    await websocket.send_text(json.dumps(greeting_response))
    logger.info(f"✅ Gabbi sent greeting for call: {call_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                request = json.loads(data)
                logger.info(f"📨 Gabbi processing: {request.get('interaction_type')} for call: {call_id}")
                
                response_data = await gabbi_agent.process_retell_request(request, call_id)
                
                if response_data:
                    await websocket.send_text(json.dumps(response_data))
                    logger.info(f"🎯 Gabbi responded: {response_data.get('content', '')[:100]}...")
                    
            except json.JSONDecodeError:
                logger.error(f"❌ JSON parse error for call: {call_id}")
                continue
            except Exception as e:
                logger.error(f"❌ Error processing call {call_id}: {e}")
                continue
                
    except WebSocketDisconnect:
        logger.info(f"🔌 Gabbi call ended: {call_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for call {call_id}: {e}")
    finally:
        # Cleanup
        gabbi_agent.conversation_memory.pop(call_id, None)
        gabbi_agent.active_calls.pop(call_id, None)
        logger.info(f"🧹 Gabbi cleaned up call: {call_id}")

@app.get("/stats")
async def get_stats():
    """Get Gabbi's current statistics"""
    return JSONResponse({
        "agent_name": "Gabbi",
        "law_firm": "Tona Law", 
        "active_calls": len(gabbi_agent.active_calls),
        "voice_engine_status": "✅ SesameAI Voice Presence Active",
        "practice_areas": ["Personal Injury", "No-Fault Collection"],
        "call_details": gabbi_agent.active_calls
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Gabbi - Tona Law AI Intake Agent on {host}:{port}")
    logger.info("👩 Agent: Gabbi (Warm, Empathetic, Expressive)")
    logger.info("⚖️ Law Firm: Tona Law")
    logger.info("🎙️ Voice Technology: SesameAI Voice Presence")
    logger.info("📋 Specialties: Personal Injury & No-Fault Collection")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20
    )
