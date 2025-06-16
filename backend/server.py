from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json
import asyncio
from enum import Enum

# AI/ML Imports
import openai
from transformers import pipeline
import numpy as np
from sentence_transformers import SentenceTransformer
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize AI Components
openai.api_key = os.environ.get('OPENAI_API_KEY', 'demo-key')
sentence_model = None
try:
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    print("Sentence transformer not loaded - running in demo mode")

# Create the main app
app = FastAPI(title="EchoVerse & EgoCore - Singularity Platform", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Enums
class PlatformMode(str, Enum):
    ECHOVERSE = "echoverse"  # Light mode - identity exploration
    EGOCORE = "egocore"      # Dark mode - AI companion

class JourneyStep(str, Enum):
    ESSENCE = "essence"
    MINDSCAPE = "mindscape"
    AESTHETIC = "aesthetic"
    NARRATIVE = "narrative"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_mode: PlatformMode = PlatformMode.ECHOVERSE
    journey_progress: Dict[str, Any] = Field(default_factory=dict)
    ai_personality_state: Dict[str, Any] = Field(default_factory=dict)
    behavioral_data: List[Dict[str, Any]] = Field(default_factory=list)
    identity_profile: Dict[str, Any] = Field(default_factory=dict)

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None

class IdentityResponse(BaseModel):
    step: JourneyStep
    responses: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AIMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    mode: PlatformMode

class AIResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    response: str
    personality_traits: Dict[str, Any]
    emotion_tone: str
    suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BehaviorEvent(BaseModel):
    user_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# AI/ML Layer 1: Perception AI
class PerceptionAI:
    @staticmethod
    def analyze_text_emotion(text: str) -> Dict[str, float]:
        """Analyze emotional content of text"""
        # Simplified emotion analysis - in production use proper models
        emotions = {
            "joy": random.uniform(0, 1),
            "sadness": random.uniform(0, 1),
            "anger": random.uniform(0, 1),
            "fear": random.uniform(0, 1),
            "surprise": random.uniform(0, 1),
            "trust": random.uniform(0, 1)
        }
        return emotions
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple keyword extraction - replace with proper NLP
        words = text.lower().split()
        keywords = [word for word in words if len(word) > 4]
        return keywords[:5]

# AI/ML Layer 2: Learning AI
class LearningAI:
    @staticmethod
    async def update_user_patterns(user_id: str, behavior_data: Dict[str, Any]):
        """Update user behavioral patterns"""
        try:
            await db.user_patterns.update_one(
                {"user_id": user_id},
                {"$push": {"patterns": behavior_data}, "$set": {"updated_at": datetime.utcnow()}},
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error updating user patterns: {e}")
    
    @staticmethod
    def predict_user_needs(user_data: Dict[str, Any]) -> List[str]:
        """Predict what user might need next"""
        # Simplified prediction logic
        predictions = [
            "Explore your creative side",
            "Challenge yourself today",
            "Reflect on recent experiences",
            "Connect with your values",
            "Try something completely new"
        ]
        return random.sample(predictions, 2)

# AI/ML Layer 3: Generative AI
class GenerativeAI:
    @staticmethod
    async def generate_personalized_prompt(user_profile: Dict[str, Any], mode: PlatformMode) -> str:
        """Generate personalized prompts based on user profile"""
        if mode == PlatformMode.ECHOVERSE:
            prompts = [
                "What aspect of your identity feels most authentic today?",
                "If your values were colors, what would your palette look like?",
                "Describe a moment when you felt most aligned with yourself.",
                "What story does your heart want to tell the world?"
            ]
        else:  # EGOCORE
            prompts = [
                "What challenge would push you to grow right now?",
                "What's one belief about yourself you're ready to test?",
                "If I dared you to be bold today, what would you do?",
                "What's the most interesting thing about you that others don't see?"
            ]
        return random.choice(prompts)
    
    @staticmethod
    async def generate_ai_response(message: str, user_context: Dict[str, Any], mode: PlatformMode) -> AIResponse:
        """Generate AI companion response"""
        emotions = PerceptionAI.analyze_text_emotion(message)
        dominant_emotion = max(emotions, key=emotions.get)
        
        if mode == PlatformMode.ECHOVERSE:
            # Gentle, reflective responses
            response_templates = [
                f"I sense {dominant_emotion} in your words. That's a profound reflection.",
                "Your journey of self-discovery continues to unfold beautifully.",
                "There's wisdom in what you're sharing. Tell me more about that feeling."
            ]
            personality_traits = {"empathy": 0.9, "wisdom": 0.8, "gentleness": 0.9}
        else:  # EGOCORE
            # More direct, challenging responses
            response_templates = [
                f"Interesting that you feel {dominant_emotion}. What are you going to do about it?",
                "I see potential in you that you're not fully tapping into yet.",
                "That's one perspective. What if you flipped that completely?"
            ]
            personality_traits = {"directness": 0.8, "challenge": 0.7, "insight": 0.9}
        
        return AIResponse(
            response=random.choice(response_templates),
            personality_traits=personality_traits,
            emotion_tone=dominant_emotion,
            suggestions=LearningAI.predict_user_needs(user_context)
        )

# API Endpoints
@api_router.get("/", tags=["System"])
async def root():
    return {"message": "EchoVerse & EgoCore - Singularity Platform API", "version": "1.0.0"}

@api_router.post("/users", response_model=User, tags=["Users"])
async def create_user(user_data: UserCreate):
    """Create a new user"""
    user = User(**user_data.dict())
    try:
        await db.users.insert_one(user.dict())
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

@api_router.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: str):
    """Get user by ID"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.post("/users/{user_id}/mode", tags=["Users"])
async def switch_mode(user_id: str, mode: PlatformMode):
    """Switch between EchoVerse and EgoCore modes"""
    try:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"current_mode": mode, "updated_at": datetime.utcnow()}}
        )
        return {"message": f"Switched to {mode} mode", "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error switching mode: {str(e)}")

@api_router.post("/journey/{user_id}/step", tags=["Identity Journey"])
async def save_journey_step(user_id: str, step_data: IdentityResponse):
    """Save progress in identity journey"""
    try:
        # Update user journey progress
        await db.users.update_one(
            {"id": user_id},
            {"$set": {f"journey_progress.{step_data.step}": step_data.dict()}}
        )
        
        # Log behavior for AI learning
        await LearningAI.update_user_patterns(
            user_id, 
            {"type": "journey_step", "step": step_data.step, "data": step_data.responses}
        )
        
        return {"message": "Journey step saved", "step": step_data.step}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving journey step: {str(e)}")

@api_router.get("/journey/{user_id}/prompts", tags=["Identity Journey"])
async def get_personalized_prompts(user_id: str, mode: PlatformMode):
    """Get personalized prompts for user"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        prompt = await GenerativeAI.generate_personalized_prompt(user.get("identity_profile", {}), mode)
        return {"prompt": prompt, "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating prompts: {str(e)}")

@api_router.post("/ai/chat", response_model=AIResponse, tags=["AI Companion"])
async def chat_with_ai(message_data: AIMessage, user_id: str):
    """Chat with AI companion"""
    try:
        # Get user context
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate AI response
        ai_response = await GenerativeAI.generate_ai_response(
            message_data.message,
            user.get("identity_profile", {}),
            message_data.mode
        )
        
        # Save conversation for learning
        conversation_data = {
            "user_id": user_id,
            "user_message": message_data.message,
            "ai_response": ai_response.dict(),
            "mode": message_data.mode,
            "timestamp": datetime.utcnow()
        }
        await db.conversations.insert_one(conversation_data)
        
        # Update AI personality state based on interaction
        await LearningAI.update_user_patterns(
            user_id,
            {"type": "ai_interaction", "mode": message_data.mode, "response_traits": ai_response.personality_traits}
        )
        
        return ai_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in AI chat: {str(e)}")

@api_router.post("/behavior/track", tags=["Behavioral Analytics"])
async def track_behavior(behavior: BehaviorEvent):
    """Track user behavior for AI learning"""
    try:
        await db.behaviors.insert_one(behavior.dict())
        await LearningAI.update_user_patterns(behavior.user_id, behavior.event_data)
        return {"message": "Behavior tracked"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error tracking behavior: {str(e)}")

@api_router.get("/analytics/{user_id}/insights", tags=["Analytics"])
async def get_user_insights(user_id: str):
    """Get AI-generated insights about user"""
    try:
        # Get user patterns
        patterns = await db.user_patterns.find_one({"user_id": user_id})
        if not patterns:
            return {"insights": ["Start your journey to unlock insights"], "suggestions": []}
        
        # Generate insights (simplified)
        insights = [
            "You show strong creative tendencies in your responses",
            "Your reflection patterns suggest deep introspective capability",
            "You're building consistency in your self-exploration journey"
        ]
        
        suggestions = LearningAI.predict_user_needs(patterns.get("patterns", {}))
        
        return {"insights": insights, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating insights: {str(e)}")

# Include router
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Background task for AI learning
async def continuous_learning_task():
    """Background task for continuous AI improvement"""
    while True:
        try:
            # Analyze patterns across all users
            patterns = await db.user_patterns.find().to_list(1000)
            # Implement collective intelligence updates here
            logger.info(f"Processed {len(patterns)} user patterns for collective learning")
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Error in continuous learning: {e}")
            await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    asyncio.create_task(continuous_learning_task())
    logger.info("EchoVerse & EgoCore Singularity Platform started!")