from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class PlatformMode(str, Enum):
    ECHOVERSE = "echoverse"
    EGOCORE = "egocore"

class JourneyStep(str, Enum):
    ESSENCE = "essence"
    MINDSCAPE = "mindscape"
    AESTHETIC = "aesthetic"
    NARRATIVE = "narrative"

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"

class ConnectionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"

# Core User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    current_mode: PlatformMode = PlatformMode.ECHOVERSE
    journey_progress: Dict[str, Any] = Field(default_factory=dict)
    ai_personality_state: Dict[str, Any] = Field(default_factory=dict)
    behavioral_data: List[Dict[str, Any]] = Field(default_factory=list)
    identity_profile: Dict[str, Any] = Field(default_factory=dict)
    
    # Social features
    connections: List[str] = Field(default_factory=list)
    followers: List[str] = Field(default_factory=list)
    following: List[str] = Field(default_factory=list)
    
    # Gamification
    experience_points: int = 0
    level: int = 1
    achievements: List[str] = Field(default_factory=list)
    streak_days: int = 0
    
    # Monetization
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    subscription_expires: Optional[datetime] = None
    credits: int = 100
    
    # Privacy settings
    profile_visibility: str = "public"  # public, friends, private
    journey_sharing: bool = True
    
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_visibility: Optional[str] = None
    journey_sharing: Optional[bool] = None

# Identity Journey Models
class IdentityResponse(BaseModel):
    step: JourneyStep
    responses: Dict[str, str]
    timestamp: Optional[str] = None

# Social Models
class Connection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str
    target_id: str
    status: ConnectionStatus = ConnectionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    message: Optional[str] = None

class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content: str
    content_type: str = "text"  # text, journey, achievement, challenge
    metadata: Dict[str, Any] = Field(default_factory=dict)
    likes: List[str] = Field(default_factory=list)
    comments: List[str] = Field(default_factory=list)
    shares: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    visibility: str = "public"
    tags: List[str] = Field(default_factory=list)

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    content: str
    likes: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Challenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    difficulty: str  # easy, medium, hard, extreme
    creator_id: str
    participants: List[str] = Field(default_factory=list)
    completed_by: List[str] = Field(default_factory=list)
    reward_xp: int = 50
    reward_credits: int = 10
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    is_active: bool = True
    requirements: Dict[str, Any] = Field(default_factory=dict)

# AI Models
class AIMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    memory_type: str  # conversation, insight, pattern, relationship
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance_score: float = 0.5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0

class AIPersonality(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    mode: PlatformMode
    traits: Dict[str, float] = Field(default_factory=dict)
    memories: List[str] = Field(default_factory=list)
    relationship_score: float = 0.0
    trust_level: float = 0.5
    adaptation_rate: float = 0.1
    last_evolution: datetime = Field(default_factory=datetime.utcnow)

# Analytics Models
class UserSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    pages_visited: List[str] = Field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    mode_switches: int = 0
    ai_interactions: int = 0

class UserAnalytics(BaseModel):
    user_id: str
    total_sessions: int = 0
    total_time_minutes: int = 0
    avg_session_duration: float = 0.0
    journey_completion_rate: float = 0.0
    ai_interaction_frequency: float = 0.0
    social_engagement_score: float = 0.0
    retention_score: float = 0.0
    last_calculated: datetime = Field(default_factory=datetime.utcnow)

# Monetization Models
class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tier: SubscriptionTier
    stripe_subscription_id: Optional[str] = None
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    is_active: bool = True
    auto_renew: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transaction_type: str  # subscription, credits, premium_feature
    amount: float
    currency: str = "USD"
    stripe_payment_intent_id: Optional[str] = None
    status: str = "pending"  # pending, completed, failed, refunded
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PremiumFeature(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    required_tier: SubscriptionTier
    credit_cost: Optional[int] = None
    is_active: bool = True

# XR Models
class VirtualSpace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    creator_id: str
    environment_type: str  # cosmic, minimal, nature, abstract
    max_participants: int = 10
    current_participants: List[str] = Field(default_factory=list)
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Avatar(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    appearance: Dict[str, Any] = Field(default_factory=dict)
    animations: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Behavior Tracking
class BehaviorEvent(BaseModel):
    user_id: str
    event_type: str
    event_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# Response Models
class UserProfile(BaseModel):
    user: User
    stats: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    achievements: List[Dict[str, Any]]

class SocialFeed(BaseModel):
    posts: List[Dict[str, Any]]
    users: Dict[str, User]
    has_more: bool
    next_cursor: Optional[str] = None

class Leaderboard(BaseModel):
    category: str
    period: str  # daily, weekly, monthly, all_time
    entries: List[Dict[str, Any]]
    user_rank: Optional[int] = None