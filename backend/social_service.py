from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
from models import *

class SocialService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def discover_users(self, user_id: str, limit: int = 20) -> List[User]:
        """Discover new users to connect with"""
        # Exclude current user and existing connections
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return []
        
        exclude_ids = [user_id] + user.get("connections", []) + user.get("following", [])
        
        # Find users with similar interests or complementary journey progress
        users = await self.db.users.find({
            "id": {"$nin": exclude_ids},
            "profile_visibility": "public"
        }).limit(limit).to_list(limit)
        
        return [User(**user) for user in users]
    
    async def send_connection_request(self, requester_id: str, target_id: str, message: Optional[str] = None) -> Connection:
        """Send a connection request"""
        # Check if connection already exists
        existing = await self.db.connections.find_one({
            "$or": [
                {"requester_id": requester_id, "target_id": target_id},
                {"requester_id": target_id, "target_id": requester_id}
            ]
        })
        
        if existing:
            raise ValueError("Connection already exists")
        
        connection = Connection(
            requester_id=requester_id,
            target_id=target_id,
            message=message
        )
        
        await self.db.connections.insert_one(connection.dict())
        return connection
    
    async def accept_connection(self, connection_id: str) -> bool:
        """Accept a connection request"""
        connection = await self.db.connections.find_one({"id": connection_id})
        if not connection:
            return False
        
        # Update connection status
        await self.db.connections.update_one(
            {"id": connection_id},
            {
                "$set": {
                    "status": ConnectionStatus.ACCEPTED,
                    "accepted_at": datetime.utcnow()
                }
            }
        )
        
        # Add to both users' connection lists
        await self.db.users.update_one(
            {"id": connection["requester_id"]},
            {"$addToSet": {"connections": connection["target_id"]}}
        )
        await self.db.users.update_one(
            {"id": connection["target_id"]},
            {"$addToSet": {"connections": connection["requester_id"]}}
        )
        
        return True
    
    async def create_post(self, user_id: str, content: str, content_type: str = "text", metadata: Dict[str, Any] = None) -> Post:
        """Create a new post"""
        post = Post(
            user_id=user_id,
            content=content,
            content_type=content_type,
            metadata=metadata or {}
        )
        
        await self.db.posts.insert_one(post.dict())
        
        # Award XP for posting
        await self.award_experience(user_id, 10, "post_created")
        
        return post
    
    async def get_social_feed(self, user_id: str, limit: int = 20, cursor: Optional[str] = None) -> SocialFeed:
        """Get personalized social feed"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return SocialFeed(posts=[], users={}, has_more=False)
        
        # Get posts from connections and followed users
        relevant_user_ids = user.get("connections", []) + user.get("following", []) + [user_id]
        
        query = {
            "user_id": {"$in": relevant_user_ids},
            "visibility": {"$in": ["public", "friends"]}
        }
        
        if cursor:
            query["created_at"] = {"$lt": datetime.fromisoformat(cursor)}
        
        posts = await self.db.posts.find(query).sort("created_at", -1).limit(limit + 1).to_list(limit + 1)
        
        has_more = len(posts) > limit
        if has_more:
            posts = posts[:limit]
        
        # Get user data for posts
        user_ids = list(set([post["user_id"] for post in posts]))
        users_data = await self.db.users.find({"id": {"$in": user_ids}}).to_list(len(user_ids))
        users = {user["id"]: User(**user) for user in users_data}
        
        # Enhance posts with engagement data
        enhanced_posts = []
        for post in posts:
            post_data = {
                **post,
                "like_count": len(post.get("likes", [])),
                "comment_count": len(post.get("comments", [])),
                "user_liked": user_id in post.get("likes", [])
            }
            enhanced_posts.append(post_data)
        
        next_cursor = posts[-1]["created_at"].isoformat() if posts and has_more else None
        
        return SocialFeed(
            posts=enhanced_posts,
            users=users,
            has_more=has_more,
            next_cursor=next_cursor
        )
    
    async def like_post(self, user_id: str, post_id: str) -> bool:
        """Like or unlike a post"""
        post = await self.db.posts.find_one({"id": post_id})
        if not post:
            return False
        
        likes = post.get("likes", [])
        
        if user_id in likes:
            # Unlike
            await self.db.posts.update_one(
                {"id": post_id},
                {"$pull": {"likes": user_id}}
            )
            return False
        else:
            # Like
            await self.db.posts.update_one(
                {"id": post_id},
                {"$addToSet": {"likes": user_id}}
            )
            
            # Award XP to post owner
            await self.award_experience(post["user_id"], 5, "post_liked")
            
            return True
    
    async def create_comment(self, user_id: str, post_id: str, content: str) -> Comment:
        """Add a comment to a post"""
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content
        )
        
        await self.db.comments.insert_one(comment.dict())
        
        # Add comment ID to post
        await self.db.posts.update_one(
            {"id": post_id},
            {"$addToSet": {"comments": comment.id}}
        )
        
        # Award XP
        await self.award_experience(user_id, 15, "comment_created")
        
        return comment
    
    async def create_challenge(self, creator_id: str, title: str, description: str, category: str, difficulty: str) -> Challenge:
        """Create a new community challenge"""
        reward_multiplier = {"easy": 1, "medium": 2, "hard": 3, "extreme": 5}
        multiplier = reward_multiplier.get(difficulty, 1)
        
        challenge = Challenge(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            creator_id=creator_id,
            reward_xp=50 * multiplier,
            reward_credits=10 * multiplier
        )
        
        await self.db.challenges.insert_one(challenge.dict())
        
        # Award XP for creating challenge
        await self.award_experience(creator_id, 25, "challenge_created")
        
        return challenge
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join a challenge"""
        result = await self.db.challenges.update_one(
            {"id": challenge_id, "is_active": True},
            {"$addToSet": {"participants": user_id}}
        )
        
        return result.modified_count > 0
    
    async def complete_challenge(self, user_id: str, challenge_id: str, evidence: Dict[str, Any] = None) -> bool:
        """Mark a challenge as completed"""
        challenge = await self.db.challenges.find_one({"id": challenge_id})
        if not challenge or user_id not in challenge.get("participants", []):
            return False
        
        # Add to completed list
        await self.db.challenges.update_one(
            {"id": challenge_id},
            {"$addToSet": {"completed_by": user_id}}
        )
        
        # Award rewards
        await self.award_experience(user_id, challenge.get("reward_xp", 50), "challenge_completed")
        await self.award_credits(user_id, challenge.get("reward_credits", 10))
        
        return True
    
    async def get_leaderboard(self, category: str = "xp", period: str = "all_time", limit: int = 50) -> Leaderboard:
        """Get leaderboard for different categories"""
        
        if category == "xp":
            sort_field = "experience_points"
        elif category == "level":
            sort_field = "level"
        elif category == "streak":
            sort_field = "streak_days"
        else:
            sort_field = "experience_points"
        
        # For time periods, we'd need to aggregate data from analytics
        users = await self.db.users.find({
            "profile_visibility": "public"
        }).sort(sort_field, -1).limit(limit).to_list(limit)
        
        entries = []
        for rank, user in enumerate(users, 1):
            entries.append({
                "rank": rank,
                "user_id": user["id"],
                "username": user["username"],
                "display_name": user.get("display_name"),
                "avatar_url": user.get("avatar_url"),
                "score": user.get(sort_field, 0),
                "level": user.get("level", 1)
            })
        
        return Leaderboard(
            category=category,
            period=period,
            entries=entries
        )
    
    async def award_experience(self, user_id: str, amount: int, reason: str) -> bool:
        """Award experience points to a user"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return False
        
        new_xp = user.get("experience_points", 0) + amount
        new_level = self.calculate_level(new_xp)
        
        await self.db.users.update_one(
            {"id": user_id},
            {"$set": {"experience_points": new_xp, "level": new_level}}
        )
        
        # Check for level up achievements
        if new_level > user.get("level", 1):
            await self.unlock_achievement(user_id, f"level_{new_level}")
        
        return True
    
    async def award_credits(self, user_id: str, amount: int) -> bool:
        """Award credits to a user"""
        await self.db.users.update_one(
            {"id": user_id},
            {"$inc": {"credits": amount}}
        )
        return True
    
    async def unlock_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Unlock an achievement for a user"""
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"achievements": achievement_id}}
        )
        
        # Award bonus XP for achievements
        if result.modified_count > 0:
            await self.award_experience(user_id, 100, f"achievement_{achievement_id}")
        
        return result.modified_count > 0
    
    @staticmethod
    def calculate_level(xp: int) -> int:
        """Calculate level based on XP (exponential growth)"""
        return int((xp / 100) ** 0.5) + 1
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return {}
        
        # Count various activities
        posts_count = await self.db.posts.count_documents({"user_id": user_id})
        comments_count = await self.db.comments.count_documents({"user_id": user_id})
        challenges_completed = await self.db.challenges.count_documents({"completed_by": user_id})
        
        return {
            "level": user.get("level", 1),
            "experience_points": user.get("experience_points", 0),
            "credits": user.get("credits", 100),
            "connections_count": len(user.get("connections", [])),
            "followers_count": len(user.get("followers", [])),
            "following_count": len(user.get("following", [])),
            "posts_count": posts_count,
            "comments_count": comments_count,
            "challenges_completed": challenges_completed,
            "achievements_count": len(user.get("achievements", [])),
            "streak_days": user.get("streak_days", 0),
            "journey_completion": self.calculate_journey_completion(user.get("journey_progress", {}))
        }
    
    @staticmethod
    def calculate_journey_completion(journey_progress: Dict[str, Any]) -> float:
        """Calculate journey completion percentage"""
        total_steps = 4  # essence, mindscape, aesthetic, narrative
        completed_steps = len([step for step in journey_progress if journey_progress[step]])
        return (completed_steps / total_steps) * 100