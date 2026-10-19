import unittest
import json
import sys
import app
import config
from database import DatabaseManager

sys.stdout.reconfigure(encoding='utf-8')

class TestAgroNexAuthAndChat(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
        # Initialize DB
        app.get_db()

    def test_01_admin_login(self):
        res = self.client.post('/api/auth/login', json={
            "username": "admin",
            "password": "agronex2026"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("token", data)
        self.assertEqual(data["user"]["username"], "admin")
        print("✓ Test 1 Passed: Admin login successful.")

    def test_02_register_with_verification_key(self):
        import time
        uname = f"farmer_{int(time.time())}"
        # Register a new farmer
        res = self.client.post('/api/auth/register', json={
            "username": uname,
            "password": "mypassword123",
            "full_name": "Ramesh Patil",
            "verification_key": config.FARMER_VERIFICATION_KEY
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("ok"))
        print("✓ Test 2 Passed: Registration with Farmer Verification Key succeeded.")

        # Test login with the newly registered farmer
        login_res = self.client.post('/api/auth/login', json={
            "username": uname,
            "password": "mypassword123"
        })
        login_data = login_res.get_json()
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_data.get("ok"))
        print("✓ Test 2.1 Passed: New farmer login verified.")

    def test_03_register_invalid_key_rejected(self):
        res = self.client.post('/api/auth/register', json={
            "username": "hacker_bob",
            "password": "password123",
            "full_name": "Bob",
            "verification_key": "WRONG_KEY"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data.get("ok"))
        print("✓ Test 3 Passed: Registration with invalid key strictly rejected.")

    def test_04_chat_english(self):
        res = self.client.post('/api/chat', json={
            "message": "What is the current soil moisture and pump state?",
            "language": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("ok"))
        self.assertIn("reply", data)
        print("✓ Test 4 Passed: English Chatbot response received:\n", data["reply"][:120], "...\n")

    def test_05_chat_marathi(self):
        res = self.client.post('/api/chat', json={
            "message": "मातीचा ओलावा किती आहे आणि टोमॅटोवर करपा रोगासाठी काय फवारावे?",
            "language": "mr"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("ok"))
        self.assertIn("reply", data)
        print("✓ Test 5 Passed: Marathi Chatbot response received:\n", data["reply"][:120], "...\n")

    def test_06_chat_hindi(self):
        res = self.client.post('/api/chat', json={
            "message": "टमाटर में कौन सी बीमारी है और उसका क्या इलाज है?",
            "language": "hi"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("ok"))
        self.assertIn("reply", data)
        print("✓ Test 6 Passed: Hindi Chatbot response received:\n", data["reply"][:120], "...\n")

if __name__ == '__main__':
    unittest.main()
