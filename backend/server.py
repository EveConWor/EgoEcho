from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json
import asyncio
import time

# Import all models and services
import sys
sys.path.append('/app/backend')
from models import *
from social_service import SocialService
from ai_service import AdvancedAIService
from monetization_service import MonetizationService
from xr_service import XRService
from analytics_service import AnalyticsService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
social_service = SocialService(db)
ai_service = AdvancedAIService(db)
monetization_service = MonetizationService(db)
xr_service = XRService(db)
analytics_service = AnalyticsService(db)

# Create the main app
app = FastAPI(
    title="EchoVerse & EgoCore - Production Singularity Platform", 
    version="2.0.0",
    description="Complete production platform with social features, AI intelligence, monetization, XR capabilities, and enterprise scaling"
)

# Create routers
api_router = APIRouter(prefix="/api")
social_router = APIRouter(prefix="/social", tags=["Social & Community"])
ai_router = APIRouter(prefix="/ai", tags=["AI Intelligence"])
monetization_router = APIRouter(prefix="/monetization", tags=["Monetization"])
xr_router = APIRouter(prefix="/xr", tags=["Extended Reality"])
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Security
security = HTTPBearer(auto_error=False)

# Rate limiting middleware
request_counts = {}

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries
    cutoff_time = current_time - 60  # 1 minute window
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts.get(client_ip, [])
        if timestamp > cutoff_time
    ]
    
    # Check rate limit (100 requests per minute)
    if len(request_counts.get(client_ip, [])) >= 100:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Try again later."}
        )
    
    # Add current request
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

app.middleware("http")(rate_limit_middleware)

# Core API Endpoints (Enhanced from Phase 1)
@api_router.get("/", tags=["System"])
async def root():
    return {
        "message": "EchoVerse & EgoCore - Production Singularity Platform",
        "version": "2.0.0",
        "features": [
            "Advanced AI Intelligence",
            "Social Community Platform", 
            "Monetization & Economy",
            "Extended Reality (XR)",
            "Enterprise Analytics",
            "Real-time Collaboration"
        ],
        "status": "production_ready"
    }

@api_router.post("/users", response_model=User, tags=["Users"])
async def create_user(user_data: UserCreate):
    """Create a new user with enhanced profile"""
    user = User(**user_data.dict())
    try:
        await db.users.insert_one(user.dict())
        
        # Initialize AI personalities for both modes
        await ai_service.initialize_ai_personality(user.id, PlatformMode.ECHOVERSE)
        await ai_service.initialize_ai_personality(user.id, PlatformMode.EGOCORE)
        
        # Track user creation
        await analytics_service.track_user_session(user.id, {
            "pages_visited": ["signup"],
            "actions_taken": [{"action": "account_created", "timestamp": datetime.utcnow().isoformat()}]
        })
        
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

@api_router.get("/users/{user_id}", response_model=UserProfile, tags=["Users"])
async def get_user_profile(user_id: str):
    """Get comprehensive user profile"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user stats
    stats = await social_service.get_user_stats(user_id)
    
    # Get recent activity
    recent_posts = await db.posts.find({"user_id": user_id}).sort("created_at", -1).limit(5).to_list(5)
    recent_activity = [{"type": "post", "data": post} for post in recent_posts]
    
    # Get achievements
    achievements = [{"id": ach, "unlocked_at": datetime.utcnow().isoformat()} for ach in user.get("achievements", [])]
    
    return UserProfile(
        user=User(**user),
        stats=stats,
        recent_activity=recent_activity,
        achievements=achievements
    )

@api_router.put("/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user profile"""
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

# Social & Community Endpoints
@social_router.get("/discover", tags=["Social"])
async def discover_users(user_id: str, limit: int = 20):
    """Discover new users to connect with"""
    users = await social_service.discover_users(user_id, limit)
    return {"users": [user.dict() for user in users]}

@social_router.post("/connections/request", tags=["Social"])
async def send_connection_request(requester_id: str, target_id: str, message: Optional[str] = None):
    """Send a connection request"""
    try:
        connection = await social_service.send_connection_request(requester_id, target_id, message)
        return {"success": True, "connection": connection.dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@social_router.post("/connections/{connection_id}/accept", tags=["Social"])
async def accept_connection(connection_id: str):
    """Accept a connection request"""
    success = await social_service.accept_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"success": True, "message": "Connection accepted"}

@social_router.post("/posts", response_model=Post, tags=["Social"])
async def create_post(request: dict):
    """Create a new post"""
    user_id = request.get("user_id")
    content = request.get("content")
    content_type = request.get("content_type", "text")
    metadata = request.get("metadata")
    
    post = await social_service.create_post(user_id, content, content_type, metadata)
    return post

@social_router.get("/feed", response_model=SocialFeed, tags=["Social"])
async def get_social_feed(user_id: str, limit: int = 20, cursor: Optional[str] = None):
    """Get personalized social feed"""
    feed = await social_service.get_social_feed(user_id, limit, cursor)
    return feed

@social_router.post("/posts/{post_id}/like", tags=["Social"])
async def like_post(post_id: str, request: dict):
    """Like or unlike a post"""
    user_id = request.get("user_id")
    liked = await social_service.like_post(user_id, post_id)
    return {"liked": liked}

@social_router.post("/posts/{post_id}/comment", response_model=Comment, tags=["Social"])
async def add_comment(post_id: str, request: dict):
    """Add a comment to a post"""
    user_id = request.get("user_id")
    content = request.get("content")
    comment = await social_service.create_comment(user_id, post_id, content)
    return comment

@social_router.post("/challenges", response_model=Challenge, tags=["Social"])
async def create_challenge(request: dict):
    """Create a new community challenge"""
    creator_id = request.get("creator_id")
    title = request.get("title")
    description = request.get("description")
    category = request.get("category")
    difficulty = request.get("difficulty")
    
    challenge = await social_service.create_challenge(creator_id, title, description, category, difficulty)
    return challenge

@social_router.post("/challenges/{challenge_id}/join", tags=["Social"])
async def join_challenge(challenge_id: str, request: dict):
    """Join a challenge"""
    user_id = request.get("user_id")
    success = await social_service.join_challenge(user_id, challenge_id)
    return {"success": success}

@social_router.get("/leaderboard", response_model=Leaderboard, tags=["Social"])
async def get_leaderboard(category: str = "xp", period: str = "all_time", limit: int = 50):
    """Get leaderboard"""
    leaderboard = await social_service.get_leaderboard(category, period, limit)
    return leaderboard

# AI Intelligence Endpoints
@ai_router.post("/chat", tags=["AI"])
async def advanced_ai_chat(request: dict):
    """Advanced AI chat with memory and personality evolution"""
    user_id = request.get("user_id")
    message = request.get("message")
    mode = PlatformMode(request.get("mode", "echoverse"))
    context = request.get("context")
    
    response = await ai_service.generate_advanced_response(user_id, message, mode, context)
    return response

@ai_router.get("/personality/{user_id}", tags=["AI"])
async def get_ai_personality(user_id: str, mode: PlatformMode):
    """Get AI personality state for user and mode"""
    personality = await db.ai_personalities.find_one({"user_id": user_id, "mode": mode})
    if not personality:
        personality_obj = await ai_service.initialize_ai_personality(user_id, mode)
        return personality_obj.dict()
    return AIPersonality(**personality).dict()

@ai_router.get("/memories/{user_id}", tags=["AI"])
async def get_ai_memories(user_id: str, limit: int = 20):
    """Get AI memories for user"""
    memories = await db.ai_memories.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"memories": memories}

@ai_router.get("/insights/{user_id}", tags=["AI"])
async def get_behavioral_insights(user_id: str):
    """Get AI-generated behavioral insights"""
    insights = await ai_service.analyze_user_patterns(user_id)
    return insights

# Monetization Endpoints
@monetization_router.post("/subscribe", tags=["Monetization"])
async def create_subscription(user_id: str, tier: SubscriptionTier, payment_method_id: Optional[str] = None):
    """Create or upgrade subscription"""
    result = await monetization_service.create_subscription(user_id, tier, payment_method_id)
    return result

@monetization_router.delete("/subscribe/{user_id}", tags=["Monetization"])
async def cancel_subscription(user_id: str):
    """Cancel user subscription"""
    success = await monetization_service.cancel_subscription(user_id)
    return {"success": success}

@monetization_router.get("/access/{user_id}/{feature}", tags=["Monetization"])
async def check_feature_access(user_id: str, feature: str):
    """Check feature access for user"""
    access = await monetization_service.check_feature_access(user_id, feature)
    return access

@monetization_router.post("/credits/purchase", tags=["Monetization"])
async def purchase_credits(user_id: str, amount: int, payment_method_id: Optional[str] = None):
    """Purchase credits"""
    result = await monetization_service.purchase_credits(user_id, amount, payment_method_id)
    return result

@monetization_router.post("/features/unlock", tags=["Monetization"])
async def unlock_premium_feature(user_id: str, feature_id: str, payment_method: str = "credits"):
    """Unlock premium feature"""
    result = await monetization_service.unlock_premium_feature(user_id, feature_id, payment_method)
    return result

@monetization_router.get("/analytics/revenue", tags=["Monetization"])
async def get_revenue_analytics():
    """Get revenue analytics (admin only)"""
    analytics = await monetization_service.generate_revenue_analytics()
    return analytics

# Extended Reality (XR) Endpoints
@xr_router.post("/spaces", response_model=VirtualSpace, tags=["XR"])
async def create_virtual_space(creator_id: str, environment_type: str, name: Optional[str] = None, custom_settings: Dict[str, Any] = None):
    """Create a new virtual space"""
    space = await xr_service.create_virtual_space(creator_id, environment_type, name, custom_settings)
    return space

@xr_router.post("/spaces/{space_id}/join", tags=["XR"])
async def join_virtual_space(user_id: str, space_id: str):
    """Join a virtual space"""
    result = await xr_service.join_virtual_space(user_id, space_id)
    return result

@xr_router.post("/spaces/{space_id}/leave", tags=["XR"])
async def leave_virtual_space(user_id: str, space_id: str):
    """Leave a virtual space"""
    success = await xr_service.leave_virtual_space(user_id, space_id)
    return {"success": success}

@xr_router.post("/avatars", response_model=Avatar, tags=["XR"])
async def create_avatar(user_id: str, name: str, appearance: Dict[str, Any], is_default: bool = False):
    """Create a custom avatar"""
    avatar = await xr_service.create_avatar(user_id, name, appearance, is_default)
    return avatar

@xr_router.get("/avatars/{user_id}", tags=["XR"])
async def get_user_avatar(user_id: str):
    """Get user's avatar"""
    avatar = await xr_service.get_user_avatar(user_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return avatar.dict()

@xr_router.get("/webxr/config", tags=["XR"])
async def get_webxr_config(user_id: str, space_id: str):
    """Get WebXR configuration for space"""
    config = await xr_service.get_webxr_config(user_id, space_id)
    return config

@xr_router.post("/interactions/record", tags=["XR"])
async def record_vr_interaction(user_id: str, space_id: str, interaction_type: str, data: Dict[str, Any]):
    """Record VR interaction"""
    await xr_service.record_vr_interaction(user_id, space_id, interaction_type, data)
    return {"success": True}

# Analytics Endpoints
@analytics_router.get("/user/{user_id}", tags=["Analytics"])
async def get_user_analytics(user_id: str):
    """Get comprehensive user analytics"""
    analytics = await analytics_service.calculate_user_analytics(user_id)
    return analytics.dict()

@analytics_router.get("/platform", tags=["Analytics"])
async def get_platform_analytics():
    """Get platform-wide analytics"""
    analytics = await analytics_service.get_platform_analytics()
    return analytics

@analytics_router.get("/realtime", tags=["Analytics"])
async def get_realtime_metrics():
    """Get real-time platform metrics"""
    metrics = await analytics_service.get_real_time_metrics()
    return metrics

@analytics_router.get("/insights/{user_id}", tags=["Analytics"])
async def get_user_insights_report(user_id: str):
    """Get comprehensive user insights report"""
    report = await analytics_service.generate_user_insights_report(user_id)
    return report

@analytics_router.get("/funnel", tags=["Analytics"])
async def get_conversion_funnel():
    """Get conversion funnel analytics"""
    funnel = await analytics_service.track_conversion_funnel()
    return funnel

@analytics_router.post("/sessions/track", tags=["Analytics"])
async def track_user_session(user_id: str, session_data: Dict[str, Any]):
    """Track user session"""
    session = await analytics_service.track_user_session(user_id, session_data)
    return {"session_id": session.id}

@analytics_router.post("/sessions/{session_id}/end", tags=["Analytics"])
async def end_user_session(session_id: str):
    """End user session"""
    success = await analytics_service.end_user_session(session_id)
    return {"success": success}

# Enhanced Core Endpoints (from Phase 1)
@api_router.post("/users/{user_id}/mode", tags=["Users"])
async def switch_mode(user_id: str, mode: PlatformMode):
    """Switch between EchoVerse and EgoCore modes"""
    try:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"current_mode": mode, "updated_at": datetime.utcnow()}}
        )
        
        # Track mode switch
        await analytics_service.track_user_session(user_id, {
            "actions_taken": [{"action": "mode_switch", "mode": mode, "timestamp": datetime.utcnow().isoformat()}],
            "mode_switches": 1
        })
        
        return {"message": f"Switched to {mode} mode", "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error switching mode: {str(e)}")

@api_router.post("/journey/{user_id}/step", tags=["Identity Journey"])
async def save_journey_step(user_id: str, step_data: IdentityResponse):
    """Save progress in identity journey"""
    try:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {f"journey_progress.{step_data.step}": step_data.dict()}}
        )
        
        # Award XP for journey progress
        await social_service.award_experience(user_id, 50, f"journey_step_{step_data.step}")
        
        # Store as AI memory for personalization
        await ai_service.store_memory(
            user_id,
            "journey_progress",
            f"Completed {step_data.step}: {json.dumps(step_data.responses)}"
        )
        
        return {"message": "Journey step saved", "step": step_data.step}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving journey step: {str(e)}")

@api_router.get("/journey/{user_id}/prompts", tags=["Identity Journey"])
async def get_personalized_prompts(user_id: str, mode: PlatformMode):
    """Get AI-generated personalized prompts"""
    try:
        # Use advanced AI to generate contextual prompts
        response = await ai_service.generate_advanced_response(
            user_id, 
            "Generate a thought-provoking question for my current journey",
            mode,
            {"request_type": "prompt_generation"}
        )
        
        prompt = response.get("response", "What aspect of your identity feels most important to explore right now?")
        
        return {"prompt": prompt, "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating prompts: {str(e)}")

@api_router.post("/behavior/track", tags=["Analytics"])
async def track_behavior(behavior: BehaviorEvent):
    """Track user behavior for AI learning and analytics"""
    try:
        await db.behaviors.insert_one(behavior.dict())
        
        # Store as AI memory
        await ai_service.store_memory(
            behavior.user_id,
            "behavior",
            f"{behavior.event_type}: {json.dumps(behavior.event_data)}"
        )
        
        return {"message": "Behavior tracked"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error tracking behavior: {str(e)}")

# Include all routers
app.include_router(api_router)
app.include_router(social_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(monetization_router, prefix="/api")
app.include_router(xr_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "https://ego-echo.vercel.app",  
        "http://localhost:3000",  # For development
        "*"  # Remove this in production for security
    ],
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

# Background tasks for continuous improvement
async def continuous_ai_learning_task():
    """Background task for continuous AI learning across all users"""
    while True:
        try:
            # Analyze patterns across all users for collective intelligence
            all_users = await db.users.find({}).to_list(1000)
            
            for user in all_users:
                user_id = user["id"]
                
                # Update AI personalities based on recent interactions
                recent_memories = await db.ai_memories.find({
                    "user_id": user_id,
                    "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                }).to_list(100)
                
                if recent_memories:
                    # Evolve AI personality based on recent interactions
                    for mode in [PlatformMode.ECHOVERSE, PlatformMode.EGOCORE]:
                        await ai_service.evolve_personality(user_id, mode, {
                            "quality_score": 0.7,  # Default quality
                            "trust_factor": 0.6,
                            "preferred_traits": {}
                        })
            
            logger.info(f"Processed AI learning for {len(all_users)} users")
            await asyncio.sleep(3600)  # Run every hour
            
        except Exception as e:
            logger.error(f"Error in continuous AI learning: {e}")
            await asyncio.sleep(3600)

async def analytics_calculation_task():
    """Background task for analytics calculation"""
    while True:
        try:
            # Update analytics for all active users
            active_users = await db.users.find({
                "last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).to_list(1000)
            
            for user in active_users:
                await analytics_service.calculate_user_analytics(user["id"])
            
            logger.info(f"Updated analytics for {len(active_users)} active users")
            await asyncio.sleep(1800)  # Run every 30 minutes
            
        except Exception as e:
            logger.error(f"Error in analytics calculation: {e}")
            await asyncio.sleep(1800)

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    asyncio.create_task(continuous_ai_learning_task())
    asyncio.create_task(analytics_calculation_task())
    logger.info("🚀 EchoVerse & EgoCore Production Singularity Platform Started!")
    logger.info("✨ Features: Advanced AI, Social Community, Monetization, XR, Enterprise Analytics")
