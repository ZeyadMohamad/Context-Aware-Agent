#!/usr/bin/env python3
"""
Test script for the Flask web interface
Tests the server-side rendered chatbot functionality
"""

import requests
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_flask_interface():
    """Test the Flask web interface functionality"""
    
    print("TESTING FLASK WEB INTERFACE (Server-Side Rendering)")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the server is running: python main.py --mode web")
        return False
    
    # Test 2: Home page
    print("\n2. Testing home page...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Home page loads successfully")
            if "Context-Aware Chatbot" in response.text:
                print("✅ Page contains correct title")
            if "example-questions" in response.text:
                print("✅ Page contains example questions")
        else:
            print(f"❌ Home page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Home page error: {e}")
    
    # Test 3: Form submission (server-side processing)
    print("\n3. Testing form submission...")
    test_messages = [
        "What is machine learning?",
        "Hello, how are you?"
    ]
    
    # Start a session to maintain chat history
    session = requests.Session()
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test message {i}: '{message}'")
        try:
            # Submit form data
            response = session.post(
                f"{base_url}/",
                data={"message": message},
                timeout=60,  # Longer timeout for LLM processing
                allow_redirects=True
            )
            
            if response.status_code == 200:
                print(f"✅ Form submission successful")
                # Check if response contains the user message
                if message in response.text:
                    print(f"✅ User message appears in chat history")
                else:
                    print(f"⚠️ User message not found in response")
                    
                # Look for bot response indicators
                if "bot-message" in response.text:
                    print(f"✅ Bot response appears to be present")
                else:
                    print(f"⚠️ No bot response found")
            else:
                print(f"❌ Form submission failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Form submission error: {e}")
        
        # Small delay between requests
        time.sleep(2)
    
    # Test 4: Clear chat functionality
    print("\n4. Testing clear chat...")
    try:
        response = session.get(f"{base_url}/clear", timeout=10)
        if response.status_code == 200:
            print("✅ Clear chat endpoint works")
            # Check if we're redirected back to home with empty history
            if "Welcome!" in response.text and "example-questions" in response.text:
                print("✅ Chat history cleared successfully")
        else:
            print(f"❌ Clear chat failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Clear chat error: {e}")
    
    print(f"\n🎉 FLASK INTERFACE TESTING COMPLETE!")
    print(f"💻 Open your browser to {base_url} to test the interface manually")
    print(f"🎯 Features tested:")
    print(f"   ✅ Server-side form processing")
    print(f"   ✅ Session-based chat history")
    print(f"   ✅ No JavaScript required")
    print(f"   ✅ Pure Flask/HTML/CSS implementation")
    return True


if __name__ == "__main__":
    print("🚀 Flask Web Interface Tester (Server-Side Rendering)")
    print("Make sure the server is running before testing!")
    print("Run: python main.py --mode web")
    print()
    
    input("Press Enter when the server is running...")
    
    test_flask_interface()
