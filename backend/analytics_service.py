import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import json
from models import *

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def track_user_session(self, user_id: str, session_data: Dict[str, Any]) -> UserSession:
        """Track a user session"""
        session = UserSession(
            user_id=user_id,
            start_time=datetime.utcnow(),
            pages_visited=session_data.get("pages_visited", []),
            actions_taken=session_data.get("actions_taken", []),
            mode_switches=session_data.get("mode_switches", 0),
            ai_interactions=session_data.get("ai_interactions", 0)
        )
        
        await self.db.user_sessions.insert_one(session.dict())
        return session
    
    async def end_user_session(self, session_id: str) -> bool:
        """End a user session and calculate duration"""
        end_time = datetime.utcnow()
        
        session = await self.db.user_sessions.find_one({"id": session_id})
        if not session:
            return False
        
        start_time = session["start_time"]
        duration = int((end_time - start_time).total_seconds() / 60)
        
        await self.db.user_sessions.update_one(
            {"id": session_id},
            {
                "$set": {
                    "end_time": end_time,
                    "duration_minutes": duration
                }
            }
        )
        
        return True
    
    async def calculate_user_analytics(self, user_id: str) -> UserAnalytics:
        """Calculate comprehensive user analytics"""
        
        # Get all sessions
        sessions = await self.db.user_sessions.find({"user_id": user_id}).to_list(1000)
        
        if not sessions:
            return UserAnalytics(user_id=user_id)
        
        # Calculate metrics
        total_sessions = len(sessions)
        total_time = sum(s.get("duration_minutes", 0) for s in sessions)
        avg_duration = total_time / total_sessions if total_sessions > 0 else 0
        
        # Journey completion rate
        user = await self.db.users.find_one({"id": user_id})
        journey_progress = user.get("journey_progress", {}) if user else {}
        journey_completion = len(journey_progress) / 4.0  # 4 total steps
        
        # AI interaction frequency
        total_interactions = sum(s.get("ai_interactions", 0) for s in sessions)
        ai_frequency = total_interactions / max(total_sessions, 1)
        
        # Social engagement score
        social_score = await self.calculate_social_engagement_score(user_id)
        
        # Retention score
        retention_score = await self.calculate_retention_score(user_id, sessions)
        
        analytics = UserAnalytics(
            user_id=user_id,
            total_sessions=total_sessions,
            total_time_minutes=total_time,
            avg_session_duration=avg_duration,
            journey_completion_rate=journey_completion,
            ai_interaction_frequency=ai_frequency,
            social_engagement_score=social_score,
            retention_score=retention_score
        )
        
        # Store analytics
        await self.db.user_analytics.replace_one(
            {"user_id": user_id},
            analytics.dict(),
            upsert=True
        )
        
        return analytics
    
    async def calculate_social_engagement_score(self, user_id: str) -> float:
        """Calculate social engagement score"""
        
        # Posts created
        posts_count = await self.db.posts.count_documents({"user_id": user_id})
        
        # Comments made
        comments_count = await self.db.comments.count_documents({"user_id": user_id})
        
        # Connections
        user = await self.db.users.find_one({"id": user_id})
        connections_count = len(user.get("connections", [])) if user else 0
        
        # Challenges participated
        challenges_count = await self.db.challenges.count_documents({"participants": user_id})
        
        # Calculate weighted score
        score = (
            posts_count * 10 +
            comments_count * 5 +
            connections_count * 2 +
            challenges_count * 15
        )
        
        # Normalize to 0-100 scale
        return min(100, score / 2)
    
    async def calculate_retention_score(self, user_id: str, sessions: List[Dict[str, Any]]) -> float:
        """Calculate user retention score"""
        
        if not sessions:
            return 0.0
        
        # Days since first session
        first_session = min(sessions, key=lambda x: x["start_time"])
        days_since_start = (datetime.utcnow() - first_session["start_time"]).days
        
        if days_since_start == 0:
            return 100.0
        
        # Unique days with sessions
        session_dates = set()
        for session in sessions:
            session_dates.add(session["start_time"].date())
        
        unique_days = len(session_dates)
        
        # Calculate retention as percentage of days with activity
        retention = (unique_days / max(days_since_start, 1)) * 100
        
        return min(100, retention)
    
    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Get overall platform analytics"""
        
        # User metrics
        total_users = await self.db.users.count_documents({})
        active_users_30d = await self.db.users.count_documents({
            "last_active": {"$gte": datetime.utcnow() - timedelta(days=30)}
        })
        active_users_7d = await self.db.users.count_documents({
            "last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        # Content metrics
        total_posts = await self.db.posts.count_documents({})
        total_comments = await self.db.comments.count_documents({})
        total_challenges = await self.db.challenges.count_documents({})
        
        # Engagement metrics
        ai_conversations = await self.db.ai_memories.count_documents({"memory_type": "conversation"})
        
        # Mode distribution
        echoverse_users = await self.db.users.count_documents({"current_mode": "echoverse"})
        egocore_users = await self.db.users.count_documents({"current_mode": "egocore"})
        
        # Journey completion stats
        users_with_progress = await self.db.users.find({
            "journey_progress": {"$exists": True, "$ne": {}}
        }).to_list(1000)
        
        completion_stats = {"0": 0, "25": 0, "50": 0, "75": 0, "100": 0}
        for user in users_with_progress:
            progress = len(user.get("journey_progress", {}))
            completion_percent = int((progress / 4) * 100)
            
            if completion_percent == 0:
                completion_stats["0"] += 1
            elif completion_percent <= 25:
                completion_stats["25"] += 1
            elif completion_percent <= 50:
                completion_stats["50"] += 1
            elif completion_percent <= 75:
                completion_stats["75"] += 1
            else:
                completion_stats["100"] += 1
        
        return {
            "users": {
                "total": total_users,
                "active_30d": active_users_30d,
                "active_7d": active_users_7d,
                "retention_rate": (active_users_30d / max(total_users, 1)) * 100
            },
            "content": {
                "posts": total_posts,
                "comments": total_comments,
                "challenges": total_challenges,
                "ai_conversations": ai_conversations
            },
            "engagement": {
                "mode_distribution": {
                    "echoverse": echoverse_users,
                    "egocore": egocore_users
                },
                "journey_completion": completion_stats,
                "avg_posts_per_user": total_posts / max(total_users, 1),
                "avg_ai_conversations_per_user": ai_conversations / max(total_users, 1)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time platform metrics"""
        
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Active users in last hour
        active_users = await self.db.user_sessions.distinct("user_id", {
            "start_time": {"$gte": one_hour_ago}
        })
        
        # New signups in last hour
        new_users = await self.db.users.count_documents({
            "created_at": {"$gte": one_hour_ago}
        })
        
        # AI interactions in last hour
        ai_interactions = await self.db.ai_memories.count_documents({
            "created_at": {"$gte": one_hour_ago},
            "memory_type": "conversation"
        })
        
        # Posts in last hour
        new_posts = await self.db.posts.count_documents({
            "created_at": {"$gte": one_hour_ago}
        })
        
        return {
            "active_users_1h": len(active_users),
            "new_signups_1h": new_users,
            "ai_interactions_1h": ai_interactions,
            "new_posts_1h": new_posts,
            "timestamp": now.isoformat()
        }
    
    async def generate_user_insights_report(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive insights report for user"""
        
        # Get user analytics
        analytics = await self.calculate_user_analytics(user_id)
        
        # Get AI analysis
        from ai_service import AdvancedAIService
        ai_service = AdvancedAIService(self.db)
        patterns = await ai_service.analyze_user_patterns(user_id)
        
        # Get social stats
        from social_service import SocialService
        social_service = SocialService(self.db)
        social_stats = await social_service.get_user_stats(user_id)
        
        # Generate recommendations
        recommendations = await self.generate_personalized_recommendations(user_id, analytics, patterns, social_stats)
        
        return {
            "user_id": user_id,
            "analytics": analytics.dict(),
            "behavioral_patterns": patterns,
            "social_stats": social_stats,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def generate_personalized_recommendations(self, user_id: str, analytics: UserAnalytics, patterns: Dict[str, Any], social_stats: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations for user growth"""
        
        recommendations = []
        
        # Journey completion recommendations
        if analytics.journey_completion_rate < 0.5:
            recommendations.append("Continue your identity exploration journey - you're making great progress!")
        elif analytics.journey_completion_rate == 1.0:
            recommendations.append("Consider revisiting your journey responses to see how you've grown")
        
        # AI interaction recommendations
        if analytics.ai_interaction_frequency < 2:
            recommendations.append("Try having more conversations with your AI companion to deepen your insights")
        
        # Social engagement recommendations
        if analytics.social_engagement_score < 30:
            recommendations.append("Connect with others on similar journeys - community support accelerates growth")
        
        # Mode switching recommendations
        user = await self.db.users.find_one({"id": user_id})
        if user:
            current_mode = user.get("current_mode", "echoverse")
            if current_mode == "echoverse":
                recommendations.append("Try EgoCore mode for a different perspective on personal growth")
            else:
                recommendations.append("Switch to EchoVerse for deeper reflection and contemplation")
        
        # Session frequency recommendations
        if analytics.retention_score < 50:
            recommendations.append("Regular engagement with the platform yields the best results for personal development")
        
        # Behavioral pattern recommendations
        growth_areas = patterns.get("growth_areas", [])
        if "confidence" in growth_areas:
            recommendations.append("Focus on building confidence through small daily achievements")
        if "relationships" in growth_areas:
            recommendations.append("Practice vulnerability and authentic connection in your interactions")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def track_conversion_funnel(self) -> Dict[str, Any]:
        """Track user conversion through the platform funnel"""
        
        # Funnel stages
        stages = {
            "visitors": await self.db.user_sessions.distinct("user_id"),
            "signups": await self.db.users.find({}).to_list(10000),
            "journey_started": await self.db.users.find({
                "journey_progress": {"$exists": True, "$ne": {}}
            }).to_list(10000),
            "ai_interaction": await self.db.ai_memories.distinct("user_id"),
            "social_engagement": await self.db.posts.distinct("user_id"),
            "subscription": await self.db.users.find({
                "subscription_tier": {"$ne": "free"}
            }).to_list(10000)
        }
        
        # Calculate conversion rates
        visitors_count = len(stages["visitors"])
        funnel_data = {
            "visitors": visitors_count,
            "signups": len(stages["signups"]),
            "journey_started": len(stages["journey_started"]),
            "ai_interaction": len(stages["ai_interaction"]),
            "social_engagement": len(stages["social_engagement"]),
            "subscription": len(stages["subscription"])
        }
        
        # Calculate conversion rates
        conversion_rates = {}
        prev_count = visitors_count
        for stage, count in funnel_data.items():
            if prev_count > 0:
                conversion_rates[f"{stage}_rate"] = (count / prev_count) * 100
            prev_count = count
        
        return {
            "funnel": funnel_data,
            "conversion_rates": conversion_rates,
            "calculated_at": datetime.utcnow().isoformat()
        }