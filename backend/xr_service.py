import os
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import *

class XRService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # VR Environment templates
        self.environment_templates = {
            "cosmic": {
                "name": "Cosmic Reflection",
                "description": "A vast starfield with floating geometric shapes for deep contemplation",
                "background": "gradient_nebula",
                "lighting": "soft_cosmic",
                "objects": ["floating_crystals", "particle_streams", "constellation_map"],
                "ambient_sound": "cosmic_drone",
                "interaction_zones": ["meditation_sphere", "memory_gallery", "insight_altar"]
            },
            "minimal": {
                "name": "Minimal Void",
                "description": "Clean, minimalist space focused on pure thought and reflection",
                "background": "gradient_void",
                "lighting": "directional_soft",
                "objects": ["geometric_podium", "light_beam", "floating_text"],
                "ambient_sound": "white_noise",
                "interaction_zones": ["thought_pedestal", "question_void", "answer_beam"]
            },
            "nature": {
                "name": "Digital Forest",
                "description": "Serene digital nature environment for grounded exploration",
                "background": "forest_clearing",
                "lighting": "dappled_sunlight",
                "objects": ["digital_trees", "flowing_stream", "butterfly_swarm"],
                "ambient_sound": "nature_sounds",
                "interaction_zones": ["wisdom_tree", "reflection_pool", "growth_garden"]
            },
            "abstract": {
                "name": "Abstract Mindscape",
                "description": "Surreal abstract environment representing the unconscious mind",
                "background": "morphing_shapes",
                "lighting": "dynamic_colors",
                "objects": ["morphing_sculptures", "color_waves", "thought_fragments"],
                "ambient_sound": "ambient_synthesis",
                "interaction_zones": ["subconscious_portal", "dream_weaver", "emotion_prism"]
            }
        }
        
        # Avatar component library
        self.avatar_components = {
            "head": {
                "geometric": ["cube", "sphere", "pyramid", "crystal"],
                "organic": ["human", "abstract_human", "energy_being"],
                "symbolic": ["mask", "constellation", "flame", "void"]
            },
            "body": {
                "geometric": ["prism", "wireframe", "crystalline"],
                "organic": ["human_form", "energy_form", "flowing_robes"],
                "symbolic": ["light_body", "particle_cloud", "sacred_geometry"]
            },
            "expressions": {
                "echoverse": ["contemplative", "wise", "gentle", "curious"],
                "egocore": ["intense", "focused", "challenging", "dynamic"]
            },
            "animations": {
                "idle": ["floating", "gentle_sway", "breathing", "meditation"],
                "interaction": ["gesture", "point", "embrace", "challenge"],
                "emotion": ["joy_burst", "sadness_flow", "anger_flare", "fear_shrink"]
            }
        }
    
    async def create_virtual_space(self, creator_id: str, environment_type: str, name: str = None, custom_settings: Dict[str, Any] = None) -> VirtualSpace:
        """Create a new virtual space for identity exploration"""
        
        template = self.environment_templates.get(environment_type, self.environment_templates["cosmic"])
        
        # Generate unique name if not provided
        if not name:
            name = f"{template['name']} - {datetime.utcnow().strftime('%Y%m%d%H%M')}"
        
        # Merge template with custom settings
        metadata = {
            **template,
            **(custom_settings or {})
        }
        
        virtual_space = VirtualSpace(
            name=name,
            description=template["description"],
            creator_id=creator_id,
            environment_type=environment_type,
            metadata=metadata
        )
        
        await self.db.virtual_spaces.insert_one(virtual_space.dict())
        
        return virtual_space
    
    async def join_virtual_space(self, user_id: str, space_id: str) -> Dict[str, Any]:
        """Join a virtual space"""
        
        space = await self.db.virtual_spaces.find_one({"id": space_id})
        if not space:
            return {"error": "Virtual space not found"}
        
        current_participants = space.get("current_participants", [])
        max_participants = space.get("max_participants", 10)
        
        if len(current_participants) >= max_participants:
            return {"error": "Virtual space is full"}
        
        if user_id in current_participants:
            return {"error": "Already in virtual space"}
        
        # Add user to space
        await self.db.virtual_spaces.update_one(
            {"id": space_id},
            {"$addToSet": {"current_participants": user_id}}
        )
        
        # Get user's avatar
        avatar = await self.get_user_avatar(user_id)
        
        # Generate spawn position
        spawn_position = self.generate_spawn_position(len(current_participants))
        
        return {
            "success": True,
            "space": VirtualSpace(**space),
            "avatar": avatar,
            "spawn_position": spawn_position,
            "participant_count": len(current_participants) + 1
        }
    
    async def leave_virtual_space(self, user_id: str, space_id: str) -> bool:
        """Leave a virtual space"""
        
        result = await self.db.virtual_spaces.update_one(
            {"id": space_id},
            {"$pull": {"current_participants": user_id}}
        )
        
        return result.modified_count > 0
    
    async def create_avatar(self, user_id: str, name: str, appearance: Dict[str, Any], is_default: bool = False) -> Avatar:
        """Create a custom avatar for user"""
        
        # Set existing avatars as non-default if this is the new default
        if is_default:
            await self.db.avatars.update_many(
                {"user_id": user_id},
                {"$set": {"is_default": False}}
            )
        
        avatar = Avatar(
            user_id=user_id,
            name=name,
            appearance=appearance,
            is_default=is_default
        )
        
        await self.db.avatars.insert_one(avatar.dict())
        
        return avatar
    
    async def get_user_avatar(self, user_id: str) -> Optional[Avatar]:
        """Get user's default avatar or create one"""
        
        # Try to get default avatar
        avatar_data = await self.db.avatars.find_one({
            "user_id": user_id,
            "is_default": True
        })
        
        if avatar_data:
            return Avatar(**avatar_data)
        
        # Create default avatar if none exists
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return None
        
        mode = user.get("current_mode", "echoverse")
        default_appearance = self.generate_default_avatar_appearance(mode)
        
        avatar = await self.create_avatar(
            user_id=user_id,
            name=f"{user.get('username', 'User')} Avatar",
            appearance=default_appearance,
            is_default=True
        )
        
        return avatar
    
    def generate_default_avatar_appearance(self, mode: str) -> Dict[str, Any]:
        """Generate default avatar appearance based on user's mode"""
        
        if mode == "echoverse":
            return {
                "head": {
                    "type": "sphere",
                    "material": "cosmic_glass",
                    "color": "#667eea",
                    "effects": ["gentle_glow", "particle_trail"]
                },
                "body": {
                    "type": "energy_form",
                    "material": "flowing_energy",
                    "color": "#764ba2",
                    "effects": ["soft_flow", "light_wisps"]
                },
                "expressions": ["contemplative", "wise"],
                "animations": {
                    "idle": "gentle_sway",
                    "interaction": "embrace",
                    "emotion": "joy_burst"
                }
            }
        else:  # egocore
            return {
                "head": {
                    "type": "crystal",
                    "material": "sharp_crystal",
                    "color": "#ff6b6b",
                    "effects": ["intense_glow", "energy_sparks"]
                },
                "body": {
                    "type": "crystalline",
                    "material": "angular_crystal",
                    "color": "#feca57",
                    "effects": ["edge_glow", "power_aura"]
                },
                "expressions": ["intense", "challenging"],
                "animations": {
                    "idle": "focused_stance",
                    "interaction": "challenge",
                    "emotion": "anger_flare"
                }
            }
    
    def generate_spawn_position(self, participant_index: int) -> Dict[str, float]:
        """Generate spawn position for new participant"""
        
        # Arrange participants in a circle
        angle = (participant_index * 2 * 3.14159) / 8  # Max 8 in circle
        radius = 5.0
        
        return {
            "x": radius * math.cos(angle),
            "y": 0.0,
            "z": radius * math.sin(angle),
            "rotation_y": angle + 3.14159  # Face center
        }
    
    async def create_shared_experience(self, space_id: str, experience_type: str, facilitator_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a shared VR experience in a space"""
        
        experience_templates = {
            "guided_meditation": {
                "duration": 600,  # 10 minutes
                "phases": ["preparation", "deepening", "exploration", "integration"],
                "interactions": ["breathing_sync", "shared_visualization", "group_reflection"]
            },
            "identity_ritual": {
                "duration": 900,  # 15 minutes
                "phases": ["circle_formation", "sharing", "transformation", "celebration"],
                "interactions": ["truth_telling", "symbolic_action", "group_witnessing"]
            },
            "challenge_quest": {
                "duration": 1200,  # 20 minutes
                "phases": ["preparation", "challenge", "struggle", "breakthrough"],
                "interactions": ["obstacle_navigation", "peer_support", "achievement_celebration"]
            }
        }
        
        template = experience_templates.get(experience_type, experience_templates["guided_meditation"])
        
        experience = {
            "id": str(uuid.uuid4()),
            "space_id": space_id,
            "type": experience_type,
            "facilitator_id": facilitator_id,
            "template": template,
            "custom_data": data,
            "participants": [],
            "current_phase": "preparation",
            "start_time": datetime.utcnow(),
            "is_active": True
        }
        
        await self.db.shared_experiences.insert_one(experience)
        
        # Notify space participants
        space = await self.db.virtual_spaces.find_one({"id": space_id})
        if space:
            for participant_id in space.get("current_participants", []):
                await self.send_vr_notification(
                    participant_id,
                    f"New {experience_type} starting in {space['name']}",
                    {"experience_id": experience["id"], "type": "experience_invitation"}
                )
        
        return experience
    
    async def send_vr_notification(self, user_id: str, message: str, metadata: Dict[str, Any] = None):
        """Send a VR-specific notification to user"""
        
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "vr_notification",
            "message": message,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "is_read": False
        }
        
        await self.db.notifications.insert_one(notification)
    
    async def get_webxr_config(self, user_id: str, space_id: str) -> Dict[str, Any]:
        """Get WebXR configuration for user entering space"""
        
        space = await self.db.virtual_spaces.find_one({"id": space_id})
        avatar = await self.get_user_avatar(user_id)
        
        if not space or not avatar:
            return {"error": "Space or avatar not found"}
        
        # Generate WebXR scene configuration
        config = {
            "scene": {
                "background": space["metadata"]["background"],
                "lighting": space["metadata"]["lighting"],
                "ambient_sound": space["metadata"]["ambient_sound"]
            },
            "objects": [
                {
                    "type": obj_type,
                    "position": self.generate_object_position(i, len(space["metadata"]["objects"])),
                    "interactive": True
                }
                for i, obj_type in enumerate(space["metadata"]["objects"])
            ],
            "interaction_zones": [
                {
                    "name": zone,
                    "position": self.generate_zone_position(i, len(space["metadata"]["interaction_zones"])),
                    "radius": 2.0,
                    "function": self.get_zone_function(zone)
                }
                for i, zone in enumerate(space["metadata"]["interaction_zones"])
            ],
            "avatar": avatar.dict(),
            "participants": await self.get_space_participants_info(space_id),
            "controls": {
                "movement": "teleport",
                "interaction": "raycast",
                "voice_chat": True,
                "gesture_recognition": True
            }
        }
        
        return config
    
    def generate_object_position(self, index: int, total: int) -> Dict[str, float]:
        """Generate position for environment objects"""
        angle = (index * 2 * 3.14159) / total
        radius = 8.0
        
        return {
            "x": radius * math.cos(angle),
            "y": random.uniform(0.5, 3.0),
            "z": radius * math.sin(angle)
        }
    
    def generate_zone_position(self, index: int, total: int) -> Dict[str, float]:
        """Generate position for interaction zones"""
        angle = (index * 2 * 3.14159) / total
        radius = 12.0
        
        return {
            "x": radius * math.cos(angle),
            "y": 0.0,
            "z": radius * math.sin(angle)
        }
    
    def get_zone_function(self, zone_name: str) -> str:
        """Get the function/purpose of an interaction zone"""
        zone_functions = {
            "meditation_sphere": "guided_breathing",
            "memory_gallery": "memory_visualization",
            "insight_altar": "wisdom_sharing",
            "thought_pedestal": "idea_manifestation",
            "question_void": "deep_inquiry",
            "answer_beam": "revelation_space",
            "wisdom_tree": "growth_visualization",
            "reflection_pool": "self_examination",
            "growth_garden": "progress_tracking"
        }
        
        return zone_functions.get(zone_name, "general_interaction")
    
    async def get_space_participants_info(self, space_id: str) -> List[Dict[str, Any]]:
        """Get information about all participants in a space"""
        
        space = await self.db.virtual_spaces.find_one({"id": space_id})
        if not space:
            return []
        
        participant_ids = space.get("current_participants", [])
        participants = []
        
        for user_id in participant_ids:
            user = await self.db.users.find_one({"id": user_id})
            avatar = await self.get_user_avatar(user_id)
            
            if user and avatar:
                participants.append({
                    "user_id": user_id,
                    "username": user.get("username"),
                    "display_name": user.get("display_name"),
                    "avatar": avatar.dict(),
                    "current_mode": user.get("current_mode", "echoverse")
                })
        
        return participants
    
    async def record_vr_interaction(self, user_id: str, space_id: str, interaction_type: str, data: Dict[str, Any]):
        """Record VR interaction for analytics"""
        
        interaction = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "space_id": space_id,
            "interaction_type": interaction_type,
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
        await self.db.vr_interactions.insert_one(interaction)
        
        # Update user's VR engagement metrics
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"vr_interaction_count": 1},
                "$set": {"last_vr_session": datetime.utcnow()}
            }
        )
    
    async def get_vr_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get VR usage analytics for user"""
        
        # Get VR interactions
        interactions = await self.db.vr_interactions.find({
            "user_id": user_id
        }).to_list(1000)
        
        # Calculate metrics
        total_interactions = len(interactions)
        spaces_visited = len(set(i["space_id"] for i in interactions))
        
        interaction_types = {}
        for interaction in interactions:
            itype = interaction["interaction_type"]
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
        
        # Get time spent in VR (estimated)
        session_duration = 0
        if interactions:
            sessions = {}
            for interaction in interactions:
                date = interaction["timestamp"].date()
                if date not in sessions:
                    sessions[date] = []
                sessions[date].append(interaction["timestamp"])
            
            for date, timestamps in sessions.items():
                if len(timestamps) > 1:
                    session_duration += (max(timestamps) - min(timestamps)).total_seconds() / 60
        
        return {
            "total_interactions": total_interactions,
            "spaces_visited": spaces_visited,
            "interaction_types": interaction_types,
            "estimated_time_minutes": session_duration,
            "average_session_interactions": total_interactions / max(len(set(i["timestamp"].date() for i in interactions)), 1),
            "favorite_environment": self.get_most_used_environment(interactions),
            "vr_engagement_score": min(100, total_interactions * 2 + spaces_visited * 5)
        }
    
    def get_most_used_environment(self, interactions: List[Dict[str, Any]]) -> str:
        """Get the most frequently used VR environment type"""
        
        if not interactions:
            return "none"
        
        # This would require joining with virtual_spaces collection
        # For simplicity, return the most common interaction type
        interaction_types = {}
        for interaction in interactions:
            itype = interaction["interaction_type"]
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
        
        if interaction_types:
            return max(interaction_types, key=interaction_types.get)
        
        return "cosmic"

# Import math for calculations
import math
import uuid