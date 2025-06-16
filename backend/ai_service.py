import os
import asyncio
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import numpy as np
from models import *

# AI Integration - will use environment variables for real API keys
try:
    import openai
    openai.api_key = os.environ.get('OPENAI_API_KEY', 'demo-key')
    OPENAI_AVAILABLE = os.environ.get('OPENAI_API_KEY') is not None
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', 'demo-key'))
    ANTHROPIC_AVAILABLE = os.environ.get('ANTHROPIC_API_KEY') is not None
except ImportError:
    ANTHROPIC_AVAILABLE = False

class AdvancedAIService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversation_memory = {}
        self.personality_evolution_rate = 0.1
        
    async def initialize_ai_personality(self, user_id: str, mode: PlatformMode) -> AIPersonality:
        """Initialize AI personality for a user in a specific mode"""
        existing = await self.db.ai_personalities.find_one({"user_id": user_id, "mode": mode})
        if existing:
            return AIPersonality(**existing)
        
        # Initialize personality traits based on mode
        if mode == PlatformMode.ECHOVERSE:
            traits = {
                "empathy": 0.9,
                "wisdom": 0.8,
                "gentleness": 0.9,
                "curiosity": 0.7,
                "patience": 0.8,
                "depth": 0.8
            }
        else:  # EGOCORE
            traits = {
                "directness": 0.8,
                "challenge": 0.7,
                "insight": 0.9,
                "intensity": 0.6,
                "growth_focus": 0.9,
                "accountability": 0.8
            }
        
        personality = AIPersonality(
            user_id=user_id,
            mode=mode,
            traits=traits,
            relationship_score=0.0,
            trust_level=0.5
        )
        
        await self.db.ai_personalities.insert_one(personality.dict())
        return personality
    
    async def generate_advanced_response(self, user_id: str, message: str, mode: PlatformMode, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate advanced AI response with memory and personality"""
        
        # Get or initialize personality
        personality = await self.db.ai_personalities.find_one({"user_id": user_id, "mode": mode})
        if not personality:
            personality_obj = await self.initialize_ai_personality(user_id, mode)
            personality = personality_obj.dict()
        
        # Build personality description
        traits = personality.get("traits", {})
        relationship_score = personality.get("relationship_score", 0.0)
        trust_level = personality.get("trust_level", 0.5)
        
        # Generate response using fallback for now (can be upgraded with real APIs)
        response_data = self.generate_intelligent_response(message, mode, traits, relationship_score)
        
        # Store interaction as memory
        await self.store_memory(
            user_id, 
            "conversation", 
            f"User: {message}\nAI: {response_data['response']}"
        )
        
        return {
            **response_data,
            "personality_state": traits,
            "relationship_score": relationship_score,
            "trust_level": trust_level
        }
    
    async def store_memory(self, user_id: str, memory_type: str, content: str, metadata: Dict[str, Any] = None) -> AIMemory:
        """Store a memory for AI to recall later"""
        memory = AIMemory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            importance_score=self.calculate_importance_score(content, metadata)
        )
        
        await self.db.ai_memories.insert_one(memory.dict())
        return memory
    
    def generate_intelligent_response(self, message: str, mode: PlatformMode, traits: Dict[str, float], relationship_score: float) -> Dict[str, Any]:
        """Generate intelligent response based on personality traits"""
        
        # Emotion analysis
        emotions = self.analyze_emotion_tone(message)
        dominant_emotion = max(emotions, key=emotions.get)
        
        if mode == PlatformMode.ECHOVERSE:
            empathy_level = traits.get("empathy", 0.8)
            wisdom_level = traits.get("wisdom", 0.8)
            
            if dominant_emotion in ["sadness", "fear"]:
                responses = [
                    f"I sense {dominant_emotion} in your words. That's completely valid and human.",
                    f"Your feelings of {dominant_emotion} show your depth and authenticity.",
                    f"There's wisdom in acknowledging {dominant_emotion}. What does it teach you?"
                ]
            elif dominant_emotion == "joy":
                responses = [
                    f"Your {dominant_emotion} radiates through your message. How beautiful!",
                    f"I can feel the lightness in your words. Joy transforms everything, doesn't it?",
                    f"This {dominant_emotion} you're experiencing - savor it, let it teach you."
                ]
            else:
                responses = [
                    "Your journey of self-discovery continues to unfold beautifully.",
                    "There's profound wisdom in what you're sharing.",
                    "I see the depth of your reflection. Tell me more about what resonates."
                ]
                
            # Relationship-based adjustments
            if relationship_score > 0.5:
                responses = [r + " I've noticed your growth through our conversations." for r in responses]
            
        else:  # EGOCORE
            directness_level = traits.get("directness", 0.8)
            challenge_level = traits.get("challenge", 0.7)
            
            if dominant_emotion in ["fear", "sadness"]:
                responses = [
                    f"So you're feeling {dominant_emotion}. What are you going to do about it?",
                    f"That {dominant_emotion} is information. How will you use it to grow?",
                    f"Interesting that you feel {dominant_emotion}. What's it protecting you from?"
                ]
            elif dominant_emotion == "anger":
                responses = [
                    "That fire in you - channel it. What needs to change?",
                    "Anger often masks deeper truths. What's really going on?",
                    "Good. Use that energy. What boundaries need setting?"
                ]
            else:
                responses = [
                    "I see potential in you that you're not fully tapping into yet.",
                    "That's one perspective. What if you flipped that completely?",
                    "What's the story you're telling yourself? Is it serving you?"
                ]
                
            # Relationship-based adjustments
            if relationship_score > 0.5:
                responses = [r + " I've seen you handle harder challenges." for r in responses]
        
        selected_response = random.choice(responses)
        suggestions = self.generate_contextual_suggestions(message, mode)
        
        return {
            "response": selected_response,
            "emotion_tone": dominant_emotion,
            "suggestions": suggestions,
            "source": "advanced_ai"
        }
    
    def analyze_emotion_tone(self, text: str) -> Dict[str, float]:
        """Advanced emotion analysis"""
        # Enhanced emotion keywords
        emotion_keywords = {
            "joy": ["happy", "excited", "amazing", "wonderful", "great", "love", "awesome", "fantastic"],
            "sadness": ["sad", "down", "depressed", "lonely", "hurt", "pain", "crying", "grief"],
            "anger": ["angry", "mad", "furious", "irritated", "frustrated", "annoyed", "rage"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "terrified", "panic"],
            "surprise": ["surprised", "shocked", "unexpected", "sudden", "wow", "amazing"],
            "trust": ["trust", "confident", "secure", "safe", "reliable", "certain"],
            "anticipation": ["excited", "looking forward", "can't wait", "hoping", "expecting"]
        }
        
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = score / max(len(keywords), 1)
        
        # Add randomness for more natural responses
        for emotion in emotions:
            emotions[emotion] += random.uniform(0, 0.3)
        
        return emotions
    
    def generate_contextual_suggestions(self, message: str, mode: PlatformMode) -> List[str]:
        """Generate contextual suggestions based on message content"""
        
        if mode == PlatformMode.ECHOVERSE:
            base_suggestions = [
                "Explore this feeling deeper",
                "What would your wisest self say?",
                "How does this connect to your values?",
                "What patterns do you notice?",
                "Reflect on this in your journey"
            ]
        else:
            base_suggestions = [
                "Challenge this assumption",
                "What's your next bold move?",
                "How can you level up here?",
                "What would courage look like?",
                "Turn this into action"
            ]
        
        # Add message-specific suggestions
        message_lower = message.lower()
        if "afraid" in message_lower or "scared" in message_lower:
            if mode == PlatformMode.ECHOVERSE:
                base_suggestions.append("Fear often shows us what matters most")
            else:
                base_suggestions.append("Face the fear - it's just information")
                
        if "confused" in message_lower or "don't know" in message_lower:
            if mode == PlatformMode.ECHOVERSE:
                base_suggestions.append("Sit with the uncertainty for a moment")
            else:
                base_suggestions.append("Test one hypothesis at a time")
        
        return random.sample(base_suggestions, min(3, len(base_suggestions)))
    
    def calculate_importance_score(self, content: str, metadata: Dict[str, Any] = None) -> float:
        """Calculate importance score for memory storage"""
        base_score = 0.5
        
        # Length factor
        if len(content) > 100:
            base_score += 0.2
        
        # Emotional intensity
        emotions = self.analyze_emotion_tone(content)
        max_emotion = max(emotions.values()) if emotions else 0
        base_score += max_emotion * 0.3
        
        # Keywords that suggest importance
        important_keywords = ["breakthrough", "realize", "understand", "important", "significant", "remember"]
        keyword_score = sum(1 for keyword in important_keywords if keyword in content.lower())
        base_score += keyword_score * 0.1
        
        return min(1.0, base_score)
    
    async def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavioral patterns for insights"""
        
        # Get user's conversation history
        memories = await self.db.ai_memories.find({
            "user_id": user_id,
            "memory_type": "conversation"
        }).to_list(100)
        
        if not memories:
            return {"patterns": [], "insights": [], "recommendations": []}
        
        # Analyze patterns
        patterns = {
            "communication_style": self.analyze_communication_style(memories),
            "emotional_patterns": self.analyze_emotional_patterns(memories),
            "growth_areas": self.identify_growth_areas(memories),
            "interaction_frequency": len(memories)
        }
        
        # Generate insights
        insights = self.generate_behavioral_insights(patterns)
        recommendations = self.generate_personalized_recommendations(patterns)
        
        return {
            "patterns": patterns,
            "insights": insights,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def analyze_communication_style(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how user communicates"""
        total_words = 0
        question_count = 0
        emotional_expressions = 0
        
        for memory in memories:
            content = memory.get("content", "")
            if "User:" in content:
                user_part = content.split("User:")[1].split("AI:")[0] if "AI:" in content else content.split("User:")[1]
                words = len(user_part.split())
                total_words += words
                
                if "?" in user_part:
                    question_count += 1
                
                emotions = self.analyze_emotion_tone(user_part)
                if max(emotions.values()) > 0.3:
                    emotional_expressions += 1
        
        avg_words = total_words / max(len(memories), 1)
        question_ratio = question_count / max(len(memories), 1)
        emotional_ratio = emotional_expressions / max(len(memories), 1)
        
        return {
            "average_message_length": avg_words,
            "questioning_tendency": question_ratio,
            "emotional_expression": emotional_ratio,
            "communication_depth": "high" if avg_words > 20 else "medium" if avg_words > 10 else "low"
        }
    
    def analyze_emotional_patterns(self, memories: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze emotional patterns over time"""
        emotion_history = []
        
        for memory in memories:
            content = memory.get("content", "")
            if "User:" in content:
                user_part = content.split("User:")[1].split("AI:")[0] if "AI:" in content else content.split("User:")[1]
                emotions = self.analyze_emotion_tone(user_part)
                emotion_history.append(emotions)
        
        # Calculate average emotions
        if not emotion_history:
            return {}
        
        avg_emotions = {}
        for emotion in emotion_history[0].keys():
            avg_emotions[emotion] = sum(e.get(emotion, 0) for e in emotion_history) / len(emotion_history)
        
        return avg_emotions
    
    def identify_growth_areas(self, memories: List[Dict[str, Any]]) -> List[str]:
        """Identify areas for potential growth"""
        growth_areas = []
        
        # Analyze for recurring themes
        recurring_topics = ["fear", "confidence", "relationships", "purpose", "creativity", "change"]
        topic_counts = {}
        
        for memory in memories:
            content = memory.get("content", "").lower()
            for topic in recurring_topics:
                if topic in content:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Identify top recurring themes as growth areas
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            if count >= 2:  # Minimum threshold
                growth_areas.append(topic)
        
        return growth_areas
    
    def generate_behavioral_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights based on behavioral patterns"""
        insights = []
        
        comm_style = patterns.get("communication_style", {})
        emotional_patterns = patterns.get("emotional_patterns", {})
        
        # Communication insights
        if comm_style.get("communication_depth") == "high":
            insights.append("You engage in deep, thoughtful communication")
        
        if comm_style.get("questioning_tendency", 0) > 0.5:
            insights.append("You're naturally curious and ask meaningful questions")
        
        # Emotional insights
        if emotional_patterns:
            dominant_emotion = max(emotional_patterns, key=emotional_patterns.get)
            if emotional_patterns[dominant_emotion] > 0.4:
                insights.append(f"You tend to express {dominant_emotion} frequently in conversations")
        
        # Growth insights
        growth_areas = patterns.get("growth_areas", [])
        if growth_areas:
            insights.append(f"You're actively working on: {', '.join(growth_areas)}")
        
        return insights
    
    def generate_personalized_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        comm_style = patterns.get("communication_style", {})
        growth_areas = patterns.get("growth_areas", [])
        
        # Communication-based recommendations
        if comm_style.get("emotional_expression", 0) < 0.3:
            recommendations.append("Try expressing your emotions more openly in conversations")
        
        # Growth area recommendations
        if "fear" in growth_areas:
            recommendations.append("Consider exploring what fear is trying to protect or teach you")
        
        if "confidence" in growth_areas:
            recommendations.append("Practice acknowledging your accomplishments and strengths")
        
        if "relationships" in growth_areas:
            recommendations.append("Focus on deepening connections through vulnerability and authenticity")
        
        # Default recommendations
        if len(recommendations) == 0:
            recommendations = [
                "Continue your journey of self-discovery",
                "Experiment with new perspectives and approaches",
                "Practice self-reflection and mindfulness"
            ]
        
        return recommendations[:3]  # Limit to top 3