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

    def test_ai_chat(self):
        """Test AI chat functionality"""
        if not self.user_id:
            print("❌ Cannot test ai_chat: No user ID available")
            return False, None
        
        # Test EchoVerse chat
        success_echo, _ = self.run_test(
            "AI Chat - EchoVerse",
            "POST",
            f"ai/chat",
            200,
            data={
                "message": "I'm feeling reflective today",
                "mode": "echoverse",
                "context": {"test": True}
            },
            params={"user_id": self.user_id}
        )
        
        # Test EgoCore chat
        success_ego, _ = self.run_test(
            "AI Chat - EgoCore",
            "POST",
            f"ai/chat",
            200,
            data={
                "message": "I need a challenge to grow",
                "mode": "egocore",
                "context": {"test": True}
            },
            params={"user_id": self.user_id}
        )
        
        return success_echo and success_ego, None

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

    def test_get_insights(self):
        """Test getting user insights"""
        if not self.user_id:
            print("❌ Cannot test get_insights: No user ID available")
            return False, None
        
        return self.run_test(
            "Get User Insights",
            "GET",
            f"analytics/{self.user_id}/insights",
            200
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting EchoVerse & EgoCore API Tests")
        print("=========================================")
        
        self.test_api_root()
        self.test_create_user()
        self.test_get_user()
        self.test_switch_mode()
        self.test_journey_step()
        self.test_get_prompts()
        self.test_ai_chat()
        self.test_track_behavior()
        self.test_get_insights()
        
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