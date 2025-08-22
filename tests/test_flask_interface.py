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
    
    base_url = "http://localhost:5000"
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code != 200:
            print(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Cannot connect to server: {e}")
        print("Make sure the server is running: python main.py --mode web")
        return False
    
    # Test 2: Home page
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code != 200:
            print(f"Home page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Home page error: {e}")
    
    # Test 3: Form submission (server-side processing)
    test_messages = [
        "What is machine learning?",
        "Hello, how are you?"
    ]
    
    # Start a session to maintain chat history
    session = requests.Session()
    
    for i, message in enumerate(test_messages, 1):
        try:
            # Submit form data
            response = session.post(
                f"{base_url}/",
                data={"message": message},
                timeout=60,  # Longer timeout for LLM processing
                allow_redirects=True
            )
            
            if response.status_code != 200:
                print(f"Form submission failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Form submission error: {e}")
        
        # Small delay between requests
        time.sleep(2)
    
    # Test 4: Clear chat functionality
    try:
        response = session.get(f"{base_url}/clear", timeout=10)
        if response.status_code != 200:
            print(f"Clear chat failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Clear chat error: {e}")
    
    return True


if __name__ == "__main__":
    print("Make sure the server is running before testing!")
    print("Run: python main.py --mode web")
    
    input("Press Enter when the server is running...")
    
    test_flask_interface()
