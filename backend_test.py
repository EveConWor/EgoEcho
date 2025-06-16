import requests
import sys
import uuid
import json
from datetime import datetime

class EchoVerseAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.user_id = None
        self.post_id = None
        self.challenge_id = None
        self.space_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                    self.test_results.append({
                        "name": name,
                        "status": "PASS",
                        "response": response_data
                    })
                    return success, response_data
                except:
                    print(f"Response: {response.text}")
                    self.test_results.append({
                        "name": name,
                        "status": "PASS",
                        "response": response.text
                    })
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append({
                    "name": name,
                    "status": "FAIL",
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "response": response.text
                })
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, None

    # Core API Tests
    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test(
            "API Root",
            "GET",
            "",
            200
        )

    def test_create_user(self):
        """Test user creation"""
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        success, response = self.run_test(
            "Create User",
            "POST",
            "users",
            200,
            data={"username": username, "email": f"{username}@test.com"}
        )
        
        if success and response and 'id' in response:
            self.user_id = response['id']
            print(f"Created test user with ID: {self.user_id}")
        
        return success, response

    def test_get_user(self):
        """Test getting user by ID"""
        if not self.user_id:
            print("❌ Cannot test get_user: No user ID available")
            return False, None
        
        return self.run_test(
            "Get User",
            "GET",
            f"users/{self.user_id}",
            200
        )

    def test_update_user(self):
        """Test updating user profile"""
        if not self.user_id:
            print("❌ Cannot test update_user: No user ID available")
            return False, None
        
        return self.run_test(
            "Update User",
            "PUT",
            f"users/{self.user_id}",
            200,
            data={
                "display_name": "Test User Updated",
                "bio": "This is a test bio for API testing"
            }
        )

    def test_switch_mode(self):
        """Test switching between EchoVerse and EgoCore modes"""
        if not self.user_id:
            print("❌ Cannot test switch_mode: No user ID available")
            return False, None
        
        # Test switching to EgoCore
        success_ego, _ = self.run_test(
            "Switch to EgoCore Mode",
            "POST",
            f"users/{self.user_id}/mode",
            200,
            params={"mode": "egocore"}
        )
        
        # Test switching back to EchoVerse
        success_echo, _ = self.run_test(
            "Switch to EchoVerse Mode",
            "POST",
            f"users/{self.user_id}/mode",
            200,
            params={"mode": "echoverse"}
        )
        
        return success_ego and success_echo, None

    def test_journey_step(self):
        """Test saving journey step"""
        if not self.user_id:
            print("❌ Cannot test journey_step: No user ID available")
            return False, None
        
        step_data = {
            "step": "essence",
            "responses": {
                "0": "I am unique because of my creativity",
                "1": "I feel most authentic when creating",
                "2": "My core values are honesty and compassion",
                "3": "I want to be remembered for helping others"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Save Journey Step",
            "POST",
            f"journey/{self.user_id}/step",
            200,
            data=step_data
        )

    def test_get_prompts(self):
        """Test getting personalized prompts"""
        if not self.user_id:
            print("❌ Cannot test get_prompts: No user ID available")
            return False, None
        
        # Test EchoVerse prompts
        success_echo, _ = self.run_test(
            "Get EchoVerse Prompts",
            "GET",
            f"journey/{self.user_id}/prompts",
            200,
            params={"mode": "echoverse"}
        )
        
        # Test EgoCore prompts
        success_ego, _ = self.run_test(
            "Get EgoCore Prompts",
            "GET",
            f"journey/{self.user_id}/prompts",
            200,
            params={"mode": "egocore"}
        )
        
        return success_echo and success_ego, None

    # Social Feature Tests
    def test_create_post(self):
        """Test creating a social post"""
        if not self.user_id:
            print("❌ Cannot test create_post: No user ID available")
            return False, None
        
        success, response = self.run_test(
            "Create Social Post",
            "POST",
            "social/posts",
            200,
            data={
                "user_id": self.user_id,
                "content": "This is a test post from API testing",
                "content_type": "text"
            }
        )
        
        if success and response and 'id' in response:
            self.post_id = response['id']
            print(f"Created test post with ID: {self.post_id}")
        
        return success, response

    def test_get_social_feed(self):
        """Test getting social feed"""
        if not self.user_id:
            print("❌ Cannot test get_social_feed: No user ID available")
            return False, None
        
        return self.run_test(
            "Get Social Feed",
            "GET",
            "social/feed",
            200,
            params={"user_id": self.user_id, "limit": 10}
        )

    def test_like_post(self):
        """Test liking a post"""
        if not self.user_id or not self.post_id:
            print("❌ Cannot test like_post: No user ID or post ID available")
            return False, None
        
        return self.run_test(
            "Like Post",
            "POST",
            f"social/posts/{self.post_id}/like",
            200,
            data={"user_id": self.user_id}
        )

    def test_comment_on_post(self):
        """Test commenting on a post"""
        if not self.user_id or not self.post_id:
            print("❌ Cannot test comment_on_post: No user ID or post ID available")
            return False, None
        
        return self.run_test(
            "Comment on Post",
            "POST",
            f"social/posts/{self.post_id}/comment",
            200,
            data={
                "user_id": self.user_id,
                "content": "This is a test comment from API testing"
            }
        )

    def test_create_challenge(self):
        """Test creating a community challenge"""
        if not self.user_id:
            print("❌ Cannot test create_challenge: No user ID available")
            return False, None
        
        success, response = self.run_test(
            "Create Challenge",
            "POST",
            "social/challenges",
            200,
            data={
                "creator_id": self.user_id,
                "title": "Test Challenge",
                "description": "This is a test challenge from API testing",
                "category": "personal_growth",
                "difficulty": "medium"
            }
        )
        
        if success and response and 'id' in response:
            self.challenge_id = response['id']
            print(f"Created test challenge with ID: {self.challenge_id}")
        
        return success, response

    def test_join_challenge(self):
        """Test joining a challenge"""
        if not self.user_id or not self.challenge_id:
            print("❌ Cannot test join_challenge: No user ID or challenge ID available")
            return False, None
        
        return self.run_test(
            "Join Challenge",
            "POST",
            f"social/challenges/{self.challenge_id}/join",
            200,
            data={"user_id": self.user_id}
        )

    def test_get_leaderboard(self):
        """Test getting leaderboard"""
        return self.run_test(
            "Get Leaderboard",
            "GET",
            "social/leaderboard",
            200,
            params={"category": "xp", "period": "all_time", "limit": 10}
        )

    # AI Feature Tests
    def test_ai_chat(self):
        """Test AI chat functionality"""
        if not self.user_id:
            print("❌ Cannot test ai_chat: No user ID available")
            return False, None
        
        # Test EchoVerse chat
        success_echo, _ = self.run_test(
            "AI Chat - EchoVerse",
            "POST",
            "ai/chat",
            200,
            data={
                "user_id": self.user_id,
                "message": "I'm feeling reflective today",
                "mode": "echoverse",
                "context": {"test": True}
            }
        )
        
        # Test EgoCore chat
        success_ego, _ = self.run_test(
            "AI Chat - EgoCore",
            "POST",
            "ai/chat",
            200,
            data={
                "user_id": self.user_id,
                "message": "I need a challenge to grow",
                "mode": "egocore",
                "context": {"test": True}
            }
        )
        
        return success_echo and success_ego, None

    def test_get_ai_personality(self):
        """Test getting AI personality"""
        if not self.user_id:
            print("❌ Cannot test get_ai_personality: No user ID available")
            return False, None
        
        # Test EchoVerse personality
        success_echo, _ = self.run_test(
            "Get AI Personality - EchoVerse",
            "GET",
            f"ai/personality/{self.user_id}",
            200,
            params={"mode": "echoverse"}
        )
        
        # Test EgoCore personality
        success_ego, _ = self.run_test(
            "Get AI Personality - EgoCore",
            "GET",
            f"ai/personality/{self.user_id}",
            200,
            params={"mode": "egocore"}
        )
        
        return success_echo and success_ego, None

    def test_get_ai_memories(self):
        """Test getting AI memories"""
        if not self.user_id:
            print("❌ Cannot test get_ai_memories: No user ID available")
            return False, None
        
        return self.run_test(
            "Get AI Memories",
            "GET",
            f"ai/memories/{self.user_id}",
            200,
            params={"limit": 10}
        )

    def test_get_behavioral_insights(self):
        """Test getting behavioral insights"""
        if not self.user_id:
            print("❌ Cannot test get_behavioral_insights: No user ID available")
            return False, None
        
        return self.run_test(
            "Get Behavioral Insights",
            "GET",
            f"ai/insights/{self.user_id}",
            200
        )

    # Monetization Feature Tests
    def test_create_subscription(self):
        """Test creating a subscription"""
        if not self.user_id:
            print("❌ Cannot test create_subscription: No user ID available")
            return False, None
        
        return self.run_test(
            "Create Subscription",
            "POST",
            "monetization/subscribe",
            200,
            data={
                "user_id": self.user_id,
                "tier": "pro",
                "payment_method_id": "test_payment_method"
            }
        )

    def test_check_feature_access(self):
        """Test checking feature access"""
        if not self.user_id:
            print("❌ Cannot test check_feature_access: No user ID available")
            return False, None
        
        return self.run_test(
            "Check Feature Access",
            "GET",
            f"monetization/access/{self.user_id}/daily_ai_interactions",
            200
        )

    def test_purchase_credits(self):
        """Test purchasing credits"""
        if not self.user_id:
            print("❌ Cannot test purchase_credits: No user ID available")
            return False, None
        
        return self.run_test(
            "Purchase Credits",
            "POST",
            "monetization/credits/purchase",
            200,
            data={
                "user_id": self.user_id,
                "amount": 100,
                "payment_method_id": "test_payment_method"
            }
        )

    def test_unlock_premium_feature(self):
        """Test unlocking a premium feature"""
        if not self.user_id:
            print("❌ Cannot test unlock_premium_feature: No user ID available")
            return False, None
        
        return self.run_test(
            "Unlock Premium Feature",
            "POST",
            "monetization/features/unlock",
            200,
            data={
                "user_id": self.user_id,
                "feature_id": "custom_avatar",
                "payment_method": "credits"
            }
        )

    # XR Feature Tests
    def test_create_virtual_space(self):
        """Test creating a virtual space"""
        if not self.user_id:
            print("❌ Cannot test create_virtual_space: No user ID available")
            return False, None
        
        success, response = self.run_test(
            "Create Virtual Space",
            "POST",
            "xr/spaces",
            200,
            data={
                "creator_id": self.user_id,
                "environment_type": "cosmic",
                "name": "Test Space",
                "custom_settings": {
                    "description": "This is a test space from API testing"
                }
            }
        )
        
        if success and response and 'id' in response:
            self.space_id = response['id']
            print(f"Created test space with ID: {self.space_id}")
        
        return success, response

    def test_join_virtual_space(self):
        """Test joining a virtual space"""
        if not self.user_id or not self.space_id:
            print("❌ Cannot test join_virtual_space: No user ID or space ID available")
            return False, None
        
        return self.run_test(
            "Join Virtual Space",
            "POST",
            f"xr/spaces/{self.space_id}/join",
            200,
            data={"user_id": self.user_id}
        )

    def test_create_avatar(self):
        """Test creating an avatar"""
        if not self.user_id:
            print("❌ Cannot test create_avatar: No user ID available")
            return False, None
        
        return self.run_test(
            "Create Avatar",
            "POST",
            "xr/avatars",
            200,
            data={
                "user_id": self.user_id,
                "name": "Test Avatar",
                "appearance": {
                    "head": {
                        "type": "sphere",
                        "color": "#667eea"
                    },
                    "body": {
                        "type": "energy_form",
                        "color": "#764ba2"
                    }
                },
                "is_default": True
            }
        )

    def test_get_webxr_config(self):
        """Test getting WebXR configuration"""
        if not self.user_id or not self.space_id:
            print("❌ Cannot test get_webxr_config: No user ID or space ID available")
            return False, None
        
        return self.run_test(
            "Get WebXR Config",
            "GET",
            "xr/webxr/config",
            200,
            params={"user_id": self.user_id, "space_id": self.space_id}
        )

    # Analytics Feature Tests
    def test_track_behavior(self):
        """Test behavior tracking"""
        if not self.user_id:
            print("❌ Cannot test track_behavior: No user ID available")
            return False, None
        
        behavior_data = {
            "user_id": self.user_id,
            "event_type": "test_event",
            "event_data": {
                "action": "test_action",
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.run_test(
            "Track Behavior",
            "POST",
            "behavior/track",
            200,
            data=behavior_data
        )

    def test_get_user_analytics(self):
        """Test getting user analytics"""
        if not self.user_id:
            print("❌ Cannot test get_user_analytics: No user ID available")
            return False, None
        
        return self.run_test(
            "Get User Analytics",
            "GET",
            f"analytics/user/{self.user_id}",
            200
        )

    def test_get_platform_analytics(self):
        """Test getting platform analytics"""
        return self.run_test(
            "Get Platform Analytics",
            "GET",
            "analytics/platform",
            200
        )

    def test_get_realtime_metrics(self):
        """Test getting realtime metrics"""
        return self.run_test(
            "Get Realtime Metrics",
            "GET",
            "analytics/realtime",
            200
        )

    def test_get_user_insights(self):
        """Test getting user insights"""
        if not self.user_id:
            print("❌ Cannot test get_user_insights: No user ID available")
            return False, None
        
        return self.run_test(
            "Get User Insights",
            "GET",
            f"analytics/insights/{self.user_id}",
            200
        )

    def test_track_user_session(self):
        """Test tracking user session"""
        if not self.user_id:
            print("❌ Cannot test track_user_session: No user ID available")
            return False, None
        
        return self.run_test(
            "Track User Session",
            "POST",
            "analytics/sessions/track",
            200,
            data={
                "user_id": self.user_id,
                "session_data": {
                    "pages_visited": ["home", "social", "premium"],
                    "actions_taken": [
                        {"action": "view_page", "page": "home", "timestamp": datetime.utcnow().isoformat()},
                        {"action": "click_button", "button": "social", "timestamp": datetime.utcnow().isoformat()}
                    ]
                }
            }
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting EchoVerse & EgoCore API Tests")
        print("=========================================")
        
        # Core API Tests
        self.test_api_root()
        self.test_create_user()
        self.test_get_user()
        self.test_update_user()
        self.test_switch_mode()
        self.test_journey_step()
        self.test_get_prompts()
        
        # Social Feature Tests
        self.test_create_post()
        self.test_get_social_feed()
        self.test_like_post()
        self.test_comment_on_post()
        self.test_create_challenge()
        self.test_join_challenge()
        self.test_get_leaderboard()
        
        # AI Feature Tests
        self.test_ai_chat()
        self.test_get_ai_personality()
        self.test_get_ai_memories()
        self.test_get_behavioral_insights()
        
        # Monetization Feature Tests
        self.test_create_subscription()
        self.test_check_feature_access()
        self.test_purchase_credits()
        self.test_unlock_premium_feature()
        
        # XR Feature Tests
        self.test_create_virtual_space()
        self.test_join_virtual_space()
        self.test_create_avatar()
        self.test_get_webxr_config()
        
        # Analytics Feature Tests
        self.test_track_behavior()
        self.test_get_user_analytics()
        self.test_get_platform_analytics()
        self.test_get_realtime_metrics()
        self.test_get_user_insights()
        self.test_track_user_session()
        
        print("\n=========================================")
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        return self.tests_passed == self.tests_run

def main():
    # Get backend URL from frontend .env
    backend_url = "https://c362172a-a576-4339-9dd2-3f26b46cbd2f.preview.emergentagent.com"
    
    print(f"Using backend URL: {backend_url}")
    
    # Run tests
    tester = EchoVerseAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())