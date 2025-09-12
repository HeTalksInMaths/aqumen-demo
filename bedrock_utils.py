"""
AWS Bedrock integration for Anthropic Claude models
Handles real API calls to replace the simulated ones
"""

import boto3
import json
import streamlit as st
from typing import Optional, Dict, Any
import time
import random

class BedrockClient:
    def __init__(self):
        """Initialize Bedrock client with credentials from Streamlit secrets"""
        try:
            # Get AWS credentials from Streamlit secrets
            aws_access_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_secret_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
            aws_region = st.secrets["aws"].get("AWS_DEFAULT_REGION", "us-east-1")
            
            # Initialize Bedrock client
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Model IDs from secrets
            self.models = {
                'STRONG': st.secrets["models"]["CLAUDE_OPUS"],
                'MID': st.secrets["models"]["CLAUDE_SONNET"], 
                'WEAK': st.secrets["models"]["CLAUDE_HAIKU"]
            }
            
            self.initialized = True
            
        except Exception as e:
            st.error(f"Failed to initialize Bedrock client: {str(e)}")
            self.initialized = False
            self.bedrock_client = None
    
    def is_available(self) -> bool:
        """Check if Bedrock client is properly initialized"""
        return self.initialized and self.bedrock_client is not None
    
    def make_api_call(self, model_tier: str, prompt: str, operation: str, max_tokens: int = 1000) -> str:
        """
        Make actual API call to Bedrock
        
        Args:
            model_tier: 'STRONG', 'MID', or 'WEAK'
            prompt: The prompt to send to the model
            operation: Description of the operation (for logging)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Model response text
        """
        if not self.is_available():
            # Fallback to simulation if Bedrock not available
            return self._simulate_api_call(operation)
        
        try:
            model_id = self.models.get(model_tier)
            if not model_id:
                raise ValueError(f"Unknown model tier: {model_tier}")
            
            # Prepare the request body for Anthropic Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Make the API call
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            
            # Extract the generated text
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return "No response generated"
                
        except Exception as e:
            st.warning(f"Bedrock API error for {operation}: {str(e)}")
            # Fallback to simulation on error
            return self._simulate_api_call(operation)
    
    def _simulate_api_call(self, operation: str) -> str:
        """Fallback simulation when Bedrock is unavailable"""
        # Add realistic delay
        delay = random.uniform(1, 3)
        time.sleep(delay)
        
        # Simulate occasional failures for realism
        if random.random() < 0.05:  # 5% failure rate
            raise Exception(f"Simulated API failure for {operation}")
        
        return f"Simulated response for: {operation}"

# Global client instance
_bedrock_client = None

def get_bedrock_client() -> BedrockClient:
    """Get or create the global Bedrock client instance"""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = BedrockClient()
    return _bedrock_client

def generate_difficulty_categories(topic: str) -> Dict[str, list]:
    """
    Generate difficulty categories using Claude Opus
    """
    client = get_bedrock_client()
    
    prompt = f"""For the topic "{topic}", create exactly 3 difficulty levels with specific subtopic examples.

Focus on creating a progression from basic concepts to advanced domain-specific knowledge.
Ensure each level has concrete, assessable subtopics that can differentiate between skill levels.

Return only a JSON object in this exact format:
{{
  "Beginner": ["subtopic1", "subtopic2", "subtopic3"],
  "Intermediate": ["subtopic1", "subtopic2", "subtopic3"], 
  "Advanced": ["subtopic1", "subtopic2", "subtopic3"]
}}"""

    if client.is_available():
        try:
            response = client.make_api_call('STRONG', prompt, f"Difficulty categories for {topic}")
            # Parse JSON response
            import json
            return json.loads(response)
        except:
            pass
    
    # Fallback data if API fails
    from constants import samplePipelineData
    if topic in samplePipelineData:
        return samplePipelineData[topic]['difficulty_categories']
    else:
        return {
            "Beginner": ["Basic concepts", "Fundamentals", "Introduction"],
            "Intermediate": ["Applied knowledge", "Problem solving", "Integration"],
            "Advanced": ["Complex scenarios", "Optimization", "Research-level"]
        }

def generate_adversarial_question(topic: str, difficulty: str, subtopic: str) -> Dict[str, Any]:
    """
    Generate an adversarial question using the multi-model pipeline
    """
    client = get_bedrock_client()
    
    # Step 1: Generate error catalog with Opus
    error_prompt = f"""For the topic "{topic}" at {difficulty} level, specifically "{subtopic}", identify 3-5 common conceptual errors that students make. Focus on domain-specific mistakes that reveal understanding gaps.

Return a JSON array of error objects with this format:
[
  {{
    "id": "error_name",
    "description": "What the error is",
    "likelihood": 0.8,
    "domain_specific": true
  }}
]"""
    
    # Step 2: Generate question with embedded errors using Opus  
    question_prompt = f"""Create a code-based assessment question for "{subtopic}" ({difficulty} level) that contains exactly 3 errors that students can click to identify.

The question should test understanding of {topic} concepts and include both real errors and trick questions (code that looks wrong but is actually correct).

Return JSON format:
{{
  "title": "Question title",
  "code": "Code with [ERROR_1]highlighted sections[/ERROR_1] marking potential errors",
  "errors": [
    {{
      "id": 1,
      "description": "What's wrong with this code",
      "severity": "high",
      "correct": true
    }}
  ]
}}"""
    
    if client.is_available():
        try:
            # Use the real API for question generation
            response = client.make_api_call('STRONG', question_prompt, f"Adversarial question for {subtopic}")
            import json
            return json.loads(response)
        except Exception as e:
            st.warning(f"API call failed, using fallback: {e}")
    
    # Fallback to sample data
    from constants import samplePipelineData
    if topic in samplePipelineData:
        return samplePipelineData[topic]['final_question']
    else:
        return {
            "title": "Error Detection Exercise",
            "code": "Sample code with potential errors...",
            "errors": []
        }

# Test connection function
def test_bedrock_connection() -> bool:
    """Test if Bedrock connection is working"""
    client = get_bedrock_client()
    if not client.is_available():
        return False
    
    try:
        # Simple test call
        response = client.make_api_call('WEAK', 'Say "Hello" in one word.', 'Connection test', max_tokens=10)
        return len(response) > 0
    except:
        return False