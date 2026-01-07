import os
from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
import base64
import json

load_dotenv()

class AIService:
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def interpret_redline(self, file_data: str, connection_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"redline_{connection_context.get('connection_id', 'default')}",
                system_message="""You are an expert structural steel detailing assistant. 
                Your role is to interpret engineer redlines on PDF drawings and extract their intent.
                You provide ADVISORY suggestions only - never authoritative approvals.
                Always indicate confidence level and reasoning."""
            ).with_model("openai", "gpt-5.2")
            
            context_str = json.dumps(connection_context, indent=2)
            prompt = f"""Analyze this engineer's redline markup for a steel connection.
            
Current Connection Context:
{context_str}

Extract the engineer's intent and suggest parameter changes.
Provide your response as JSON with:
- intent: (string) What the engineer wants to change
- parameters: (dict) Suggested parameter changes (e.g., {{"num_bolts": 6, "plate_thickness": 0.5}})
- confidence: (float 0-1) How confident you are
- reasoning: (string) Why you interpreted it this way
- warnings: (list) Any concerns or clarifications needed

Remember: Your suggestions are ADVISORY ONLY. Human approval required."""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            try:
                result = json.loads(response)
            except:
                result = {
                    "intent": response[:200],
                    "parameters": {},
                    "confidence": 0.5,
                    "reasoning": "Unable to parse structured response",
                    "warnings": ["Manual review required"]
                }
            
            return result
            
        except Exception as e:
            return {
                "intent": "Error processing redline",
                "parameters": {},
                "confidence": 0.0,
                "reasoning": f"AI service error: {str(e)}",
                "warnings": ["Manual interpretation required"]
            }
    
    async def suggest_connection_type(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id="connection_suggestion",
                system_message="""You are a structural steel connection design assistant.
                Suggest appropriate AISC-compliant connection types based on requirements.
                Your suggestions are ADVISORY - not authoritative."""
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""Based on these connection requirements:
{json.dumps(requirements, indent=2)}

Suggest the most appropriate shear connection type from:
- single_plate
- double_angle
- end_plate
- beam_to_column_shear
- beam_to_beam_shear

Provide response as JSON:
{{
  "suggested_type": "connection_type",
  "reasoning": "why this is appropriate",
  "alternatives": ["other options"],
  "initial_parameters": {{"param": value}}
}}

Advisory only - engineer review required."""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            try:
                result = json.loads(response)
            except:
                result = {
                    "suggested_type": "single_plate",
                    "reasoning": "Default suggestion - manual review needed",
                    "alternatives": ["double_angle", "end_plate"],
                    "initial_parameters": {}
                }
            
            return result
            
        except Exception as e:
            return {
                "suggested_type": "single_plate",
                "reasoning": f"Error: {str(e)}",
                "alternatives": [],
                "initial_parameters": {}
            }
    
    async def generate_rfi(self, connection_data: Dict[str, Any], issue: str) -> str:
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id="rfi_generation",
                system_message="You are a technical writing assistant for structural steel RFIs."
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""Generate a professional Request for Information (RFI) for:

Connection: {connection_data.get('name', 'Unknown')}
Type: {connection_data.get('connection_type', 'Unknown')}
Issue: {issue}

Include:
1. Clear description of the issue
2. Relevant connection parameters
3. Question for engineer
4. Suggested resolution (advisory)

Keep it professional and concise."""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            return response
            
        except Exception as e:
            return f"RFI Generation Error: {str(e)}"