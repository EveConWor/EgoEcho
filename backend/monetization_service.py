import os
import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import *

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_demo_key')
STRIPE_AVAILABLE = os.environ.get('STRIPE_SECRET_KEY') is not None

class MonetizationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Subscription pricing (in cents)
        self.pricing = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PRO: 999,  # $9.99/month
            SubscriptionTier.ELITE: 2999  # $29.99/month
        }
        
        # Feature access matrix
        self.feature_access = {
            SubscriptionTier.FREE: {
                "daily_ai_interactions": 10,
                "journey_steps": 4,
                "challenge_participation": 3,
                "social_connections": 50,
                "personality_modes": 2,
                "advanced_insights": False,
                "premium_challenges": False,
                "custom_avatars": False,
                "vr_spaces": False
            },
            SubscriptionTier.PRO: {
                "daily_ai_interactions": 100,
                "journey_steps": "unlimited",
                "challenge_participation": "unlimited",
                "social_connections": 500,
                "personality_modes": "unlimited",
                "advanced_insights": True,
                "premium_challenges": True,
                "custom_avatars": True,
                "vr_spaces": 3
            },
            SubscriptionTier.ELITE: {
                "daily_ai_interactions": "unlimited",
                "journey_steps": "unlimited", 
                "challenge_participation": "unlimited",
                "social_connections": "unlimited",
                "personality_modes": "unlimited",
                "advanced_insights": True,
                "premium_challenges": True,
                "custom_avatars": True,
                "vr_spaces": "unlimited",
                "priority_support": True,
                "api_access": True,
                "white_label": True
            }
        }
    
    async def create_subscription(self, user_id: str, tier: SubscriptionTier, payment_method_id: str = None) -> Dict[str, Any]:
        """Create a new subscription for user"""
        
        if tier == SubscriptionTier.FREE:
            # Free tier - no payment required
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                end_date=None,  # No expiration for free tier
                is_active=True
            )
            
            await self.db.subscriptions.insert_one(subscription.dict())
            await self.update_user_subscription(user_id, tier)
            
            return {
                "subscription_id": subscription.id,
                "status": "active",
                "tier": tier,
                "message": "Free tier activated"
            }
        
        if not STRIPE_AVAILABLE:
            # Demo mode - simulate payment
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                end_date=datetime.utcnow() + timedelta(days=30),
                is_active=True
            )
            
            await self.db.subscriptions.insert_one(subscription.dict())
            await self.update_user_subscription(user_id, tier)
            
            return {
                "subscription_id": subscription.id,
                "status": "active",
                "tier": tier,
                "message": "Demo subscription activated"
            }
        
        try:
            # Create Stripe customer
            user = await self.db.users.find_one({"id": user_id})
            customer = stripe.Customer.create(
                email=user.get("email"),
                metadata={"user_id": user_id}
            )
            
            # Create subscription
            price_amount = self.pricing[tier]
            stripe_subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'EchoVerse {tier.value.title()} Plan',
                        },
                        'unit_amount': price_amount,
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                }],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            
            # Save subscription to database
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                stripe_subscription_id=stripe_subscription.id,
                end_date=datetime.utcnow() + timedelta(days=30),
                is_active=stripe_subscription.status == "active"
            )
            
            await self.db.subscriptions.insert_one(subscription.dict())
            
            if subscription.is_active:
                await self.update_user_subscription(user_id, tier)
            
            return {
                "subscription_id": subscription.id,
                "stripe_subscription_id": stripe_subscription.id,
                "client_secret": stripe_subscription.latest_invoice.payment_intent.client_secret,
                "status": stripe_subscription.status,
                "tier": tier
            }
            
        except Exception as e:
            print(f"Stripe error: {e}")
            return {"error": str(e)}
    
    async def update_user_subscription(self, user_id: str, tier: SubscriptionTier):
        """Update user's subscription tier"""
        end_date = None if tier == SubscriptionTier.FREE else datetime.utcnow() + timedelta(days=30)
        
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "subscription_tier": tier,
                    "subscription_expires": end_date
                }
            }
        )
    
    async def cancel_subscription(self, user_id: str) -> bool:
        """Cancel user's subscription"""
        subscription = await self.db.subscriptions.find_one({
            "user_id": user_id,
            "is_active": True
        })
        
        if not subscription:
            return False
        
        # Cancel Stripe subscription if exists
        if subscription.get("stripe_subscription_id") and STRIPE_AVAILABLE:
            try:
                stripe.Subscription.delete(subscription["stripe_subscription_id"])
            except Exception as e:
                print(f"Error canceling Stripe subscription: {e}")
        
        # Update database
        await self.db.subscriptions.update_one(
            {"id": subscription["id"]},
            {"$set": {"is_active": False, "auto_renew": False}}
        )
        
        # Downgrade user to free tier
        await self.update_user_subscription(user_id, SubscriptionTier.FREE)
        
        return True
    
    async def check_feature_access(self, user_id: str, feature: str) -> Dict[str, Any]:
        """Check if user has access to a specific feature"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return {"access": False, "reason": "User not found"}
        
        tier = SubscriptionTier(user.get("subscription_tier", "free"))
        
        # Check if subscription is expired
        expires = user.get("subscription_expires")
        if expires and datetime.fromisoformat(expires) < datetime.utcnow():
            # Expired subscription - downgrade to free
            await self.update_user_subscription(user_id, SubscriptionTier.FREE)
            tier = SubscriptionTier.FREE
        
        feature_limits = self.feature_access.get(tier, {})
        feature_limit = feature_limits.get(feature)
        
        if feature_limit is None:
            return {"access": False, "reason": "Feature not defined"}
        
        if feature_limit is False:
            return {
                "access": False, 
                "reason": f"Feature requires {SubscriptionTier.PRO} or higher",
                "upgrade_required": True
            }
        
        if feature_limit is True or feature_limit == "unlimited":
            return {"access": True, "limit": feature_limit}
        
        # Check usage for limited features
        if isinstance(feature_limit, int):
            usage = await self.get_feature_usage(user_id, feature)
            return {
                "access": usage < feature_limit,
                "limit": feature_limit,
                "usage": usage,
                "remaining": max(0, feature_limit - usage)
            }
        
        return {"access": True, "limit": feature_limit}
    
    async def get_feature_usage(self, user_id: str, feature: str) -> int:
        """Get current feature usage for user"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if feature == "daily_ai_interactions":
            count = await self.db.ai_memories.count_documents({
                "user_id": user_id,
                "memory_type": "conversation",
                "created_at": {"$gte": today}
            })
            return count
        
        elif feature == "challenge_participation":
            count = await self.db.challenges.count_documents({
                "participants": user_id,
                "start_date": {"$gte": today}
            })
            return count
        
        elif feature == "social_connections":
            user = await self.db.users.find_one({"id": user_id})
            return len(user.get("connections", []))
        
        return 0
    
    async def purchase_credits(self, user_id: str, amount: int, payment_method_id: str = None) -> Dict[str, Any]:
        """Purchase credits for user"""
        
        # Credit pricing: 100 credits = $1
        price_cents = amount
        
        if not STRIPE_AVAILABLE:
            # Demo mode - grant credits immediately
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"credits": amount}}
            )
            
            # Record transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type="credits",
                amount=price_cents / 100,
                status="completed",
                metadata={"credits_purchased": amount}
            )
            await self.db.transactions.insert_one(transaction.dict())
            
            return {
                "transaction_id": transaction.id,
                "status": "completed",
                "credits_purchased": amount,
                "message": "Demo credits added"
            }
        
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=price_cents,
                currency='usd',
                metadata={
                    'user_id': user_id,
                    'credits': amount,
                    'type': 'credit_purchase'
                }
            )
            
            # Record transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type="credits",
                amount=price_cents / 100,
                stripe_payment_intent_id=intent.id,
                status="pending",
                metadata={"credits_to_purchase": amount}
            )
            await self.db.transactions.insert_one(transaction.dict())
            
            return {
                "transaction_id": transaction.id,
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": "pending"
            }
            
        except Exception as e:
            print(f"Stripe error: {e}")
            return {"error": str(e)}
    
    async def unlock_premium_feature(self, user_id: str, feature_id: str, payment_method: str = "credits") -> Dict[str, Any]:
        """Unlock a premium feature for user"""
        
        # Premium feature costs
        feature_costs = {
            "custom_avatar": 50,
            "premium_challenge": 25,
            "advanced_insight": 30,
            "vr_space_access": 100
        }
        
        cost = feature_costs.get(feature_id, 0)
        if cost == 0:
            return {"error": "Feature not found or free"}
        
        if payment_method == "credits":
            user = await self.db.users.find_one({"id": user_id})
            current_credits = user.get("credits", 0)
            
            if current_credits < cost:
                return {
                    "error": "Insufficient credits",
                    "required": cost,
                    "available": current_credits
                }
            
            # Deduct credits
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"credits": -cost}}
            )
            
            # Record purchase
            transaction = Transaction(
                user_id=user_id,
                transaction_type="premium_feature",
                amount=0,  # Paid with credits
                status="completed",
                metadata={
                    "feature_id": feature_id,
                    "credits_spent": cost
                }
            )
            await self.db.transactions.insert_one(transaction.dict())
            
            # Grant feature access (store in user's unlocked features)
            await self.db.users.update_one(
                {"id": user_id},
                {"$addToSet": {"unlocked_features": feature_id}}
            )
            
            return {
                "success": True,
                "feature_unlocked": feature_id,
                "credits_spent": cost,
                "remaining_credits": current_credits - cost
            }
        
        return {"error": "Invalid payment method"}
    
    async def get_user_transaction_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's transaction history"""
        transactions = await self.db.transactions.find({
            "user_id": user_id
        }).sort("created_at", -1).limit(limit).to_list(limit)
        
        return transactions
    
    async def generate_revenue_analytics(self) -> Dict[str, Any]:
        """Generate revenue analytics for platform"""
        
        # Get subscription counts
        subscription_counts = {}
        for tier in SubscriptionTier:
            count = await self.db.users.count_documents({"subscription_tier": tier})
            subscription_counts[tier.value] = count
        
        # Get transaction stats
        transactions = await self.db.transactions.find({
            "status": "completed",
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
        }).to_list(1000)
        
        monthly_revenue = sum(t.get("amount", 0) for t in transactions)
        transaction_count = len(transactions)
        
        # Get credit usage stats
        total_credits_purchased = sum(
            t.get("metadata", {}).get("credits_purchased", 0) 
            for t in transactions 
            if t.get("transaction_type") == "credits"
        )
        
        return {
            "subscription_distribution": subscription_counts,
            "monthly_revenue": monthly_revenue,
            "monthly_transactions": transaction_count,
            "total_credits_purchased": total_credits_purchased,
            "average_transaction_value": monthly_revenue / max(transaction_count, 1),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def create_promotional_code(self, code: str, discount_percent: int, tier: SubscriptionTier, expires_at: datetime) -> Dict[str, Any]:
        """Create a promotional discount code"""
        
        promo = {
            "id": str(uuid.uuid4()),
            "code": code.upper(),
            "discount_percent": discount_percent,
            "applicable_tier": tier,
            "expires_at": expires_at,
            "usage_count": 0,
            "max_uses": 100,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        await self.db.promotional_codes.insert_one(promo)
        
        return {
            "promo_id": promo["id"],
            "code": code.upper(),
            "discount": f"{discount_percent}%",
            "expires": expires_at.isoformat()
        }
    
    async def apply_promotional_code(self, user_id: str, code: str) -> Dict[str, Any]:
        """Apply promotional code to user's account"""
        
        promo = await self.db.promotional_codes.find_one({
            "code": code.upper(),
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not promo:
            return {"error": "Invalid or expired promotional code"}
        
        if promo.get("usage_count", 0) >= promo.get("max_uses", 100):
            return {"error": "Promotional code usage limit reached"}
        
        # Check if user already used this code
        existing_use = await self.db.promo_usage.find_one({
            "user_id": user_id,
            "promo_code": code.upper()
        })
        
        if existing_use:
            return {"error": "Promotional code already used"}
        
        # Apply discount (store for use during subscription creation)
        discount_data = {
            "user_id": user_id,
            "promo_code": code.upper(),
            "discount_percent": promo["discount_percent"],
            "applicable_tier": promo["applicable_tier"],
            "used_at": datetime.utcnow()
        }
        
        await self.db.promo_usage.insert_one(discount_data)
        
        # Update promo usage count
        await self.db.promotional_codes.update_one(
            {"code": code.upper()},
            {"$inc": {"usage_count": 1}}
        )
        
        return {
            "success": True,
            "discount_percent": promo["discount_percent"],
            "applicable_tier": promo["applicable_tier"],
            "message": f"{promo['discount_percent']}% discount applied!"
        }
    
    async def get_subscription_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get detailed subscription analytics for user"""
        
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return {}
        
        tier = SubscriptionTier(user.get("subscription_tier", "free"))
        
        # Calculate subscription value
        days_since_signup = (datetime.utcnow() - datetime.fromisoformat(user["created_at"])).days
        subscription_value = days_since_signup * (self.pricing.get(tier, 0) / 100) / 30  # Daily value
        
        # Get usage stats
        feature_usage = {}
        for feature in self.feature_access.get(tier, {}).keys():
            usage = await self.get_feature_usage(user_id, feature)
            feature_usage[feature] = usage
        
        # Get transaction history
        transactions = await self.get_user_transaction_history(user_id, 10)
        total_spent = sum(t.get("amount", 0) for t in transactions)
        
        return {
            "current_tier": tier.value,
            "subscription_value": subscription_value,
            "days_since_signup": days_since_signup,
            "feature_usage": feature_usage,
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "credits_balance": user.get("credits", 0),
            "subscription_expires": user.get("subscription_expires"),
            "feature_access": self.feature_access.get(tier, {})
        }