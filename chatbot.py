import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import openai
import requests
from flask import request, jsonify, Blueprint
from models import Task,Reminder,db
from app import app, update_task, delete_task, update_reminder, delete_reminder


llm_bp = Blueprint('llm', __name__)

# Set up API key
openai.api_key = "OPENAI_API_KEY"
class LLMInputProcessor:
    def __init__(self, base_url: str = 'http://127.0.0.1:5000'):
        
        self.base_url = base_url
        self.endpoints = {
            'tasks': f'{base_url}/tasks/',
            'reminders': f'{base_url}/reminders/'
        }



    def parse_llm_input(self,user_input):

        prompt = f"""
        Parse the following user input into a structured JSON object that specifies:
        1. Model type (Task or Reminder)
        2. Action (create/update/delete/read)
        3. Values for corresponding columns - name, deadline, isCompleted

        User Input: {user_input}

        JSON Schema:
        {{
            "model": "Task" or "Reminder",
            "action": "create/update/delete/read",
            "values": {{
                "name": name,
                "priority": priority,
                "deadline": deadline (if model=Task),
                "time": time (if model=Reminder),   
                "category": category                    

            }}
        }}
        """

        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that processes task and reminder CRUD operations."},
                {"role": "user", "content": prompt}
            ]
        )

        return json.loads(response.choices[0].message.content)

    @llm_bp.route("/llm", methods=["POST"])
    def llm_input(self):
        
        user_input = request.json.get('input')
        
        try:
            parsed_data = self.parse_llm_input(user_input)
            input_processor = self.process_input(parsed_data)
            
            
        except Exception as e:
            return {"error": f"Failed to process LLM response: {str(e)}"}

    def process_input(self, user_input: str) -> Dict[str, Any]:
            """
            Process natural language input and call appropriate CRUD API
            
            Args:
                user_input (str): Natural language input from user
            
            Returns:
                Dict[str, Any]: API response from CRUD operation
            """
            normalized_input = user_input.lower().strip()
            
            # Determine model type and action
            model_type, action = self._determine_model_and_action(normalized_input)
            
            # Extract specific values
            values = self._extract_values(normalized_input, model_type)
            
            # Validate and clean extracted values
            validated_values = self._validate_values(values, model_type)
            
            # Determine appropriate API endpoint and method
            endpoint = self.endpoints['tasks'] if model_type == 'Task' else self.endpoints['reminders']
            endpoint =endpoint.append(action)
            # Perform API call based on action
            try:
                if action == 'create':
                    response = requests.post(endpoint, json=validated_values)
                elif action == 'update':
                    # Assuming update requires identifying the specific record
                    search_values = {k: v for k, v in validated_values.items() if k in ['title', 'id']}
                    search_response = requests.get(f"{endpoint}/update", params=search_values)
                    
                    if search_response.status_code == 200 and search_response.json():
                        record_id = search_response.json()[0]['id']
                        response = requests.put(f"{endpoint}/{record_id}", json=validated_values)
                    else:
                        return {"error": "No matching record found for update"}
                
                elif action == 'delete':
                    # Search for record to delete
                    search_values = {k: v for k, v in validated_values.items() if k in ['title', 'id']}
                    search_response = requests.get(f"{endpoint}/search", params=search_values)
                    
                    if search_response.status_code == 200 and search_response.json():
                        record_id = search_response.json()[0]['id']
                        response = requests.delete(f"{endpoint}/{record_id}")
                    else:
                        return {"error": "No matching record found for deletion"}
                
                elif action == 'read':
                    response = requests.get(f"{endpoint}/search", params=validated_values)
                
                else:
                    return {"error": f"Unsupported action: {action}"}
                
                # Handle API response
                if response.status_code in [200, 201]:
                    return {
                        "status": "success",
                        "model": model_type,
                        "action": action,
                        "data": response.json()
                    }
                else:
                    return {
                        "status": "error",
                        "message": response.text,
                        "code": response.status_code
                    }
            
            except requests.RequestException as e:
                return {
                    "status": "error",
                    "message": f"API request failed: {str(e)}",
                    "details": str(e)
                }

    def _determine_model_and_action(self, input_text: str) -> Tuple[str, str]:
            """
            Determine model type and action from input text
            
            """
            # Existing implementation from previous artifact
            action_patterns = {
                "create": r'\b(create|add|make|new)\b',
                "update": r'\b(update|modify|change|edit)\b',
                "delete": r'\b(delete|remove|cancel)\b',
                "read": r'\b(read|find|search|get)\b'
            }
            
            model_patterns = {
                "Task": r'\b(task|todo|to-do|work item)\b',
                "Reminder": r'\b(remind|reminder|alert|notification)\b'
            }
            
            action = next(
                (action for action, pattern in action_patterns.items() 
                if re.search(pattern, input_text)),
                "create"
            )
            
            model_type = next(
                (model for model, pattern in model_patterns.items() 
                if re.search(pattern, input_text)),
                "Task"
            )
            
            return model_type, action

    def _extract_values(self, input_text: str, model_type: str) -> Dict[str, Any]:
            """
            Extract specific values based on model type
            
            Similar to previous implementation with value extraction
            """
            # Existing implementation from previous artifact
            values = {}
            
            title_match = re.search(r'"([^"]*)"', input_text)
            values['title'] = title_match.group(1) if title_match else None
            
            desc_match = re.search(r'description\s*[:]\s*"([^"]*)"', input_text)
            values['description'] = desc_match.group(1) if desc_match else None
            
            date_match = self._extract_date(input_text)
            
            # Specific model value extraction logic
            if model_type == "Task":
                priority_match = re.search(r'priority\s*[:]\s*(\d+)', input_text)
                status_match = re.search(r'status\s*[:]\s*(\w+)', input_text)
                
                values['priority'] = int(priority_match.group(1)) if priority_match else 3
                values['category'] = status_match.group(1) if status_match else 'pending'
                values['deadline'] = date_match
            
            elif model_type == "Reminder":
                category_match = re.search(r'category\s*[:]\s*(\w+)', input_text)
                
                values['reminder_time'] = date_match
                values['category'] = category_match.group(1) if category_match else 'general'
            
            return {k: v for k, v in values.items() if v is not None}

    def _extract_date(self, input_text: str) -> Optional[str]:
            """
            Extract date from input text and convert to ISO format
            
            Returns date in ISO format for API compatibility
            """
            date = self._parse_date(input_text)
            return date.isoformat() if date else None

    @staticmethod
    def _parse_date(self,input_text: str) -> Optional[datetime]:
            """
            Date parsing implementation from previous artifact
            Returns datetime object
            """
            # Relative time patterns
            relative_patterns = [
                (r'in (\d+)\s*(hour|day|week|month)s?', lambda num, unit: self._calculate_relative_time(int(num), unit)),
                (r'(tomorrow|today|next week)', self._parse_relative_date)
            ]
            
            # Specific date patterns
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',   # MM/DD/YYYY
            ]
            
            # Check relative time patterns first
            for pattern, handler in relative_patterns:
                match = re.search(pattern, input_text, re.IGNORECASE)
                if match:
                    return handler(*match.groups())
            
            # Check specific date patterns
            for pattern in date_patterns:
                match = re.search(pattern, input_text)
                if match:
                    try:
                        return datetime.strptime(match.group(0), '%Y-%m-%d')
                    except ValueError:
                        try:
                            return datetime.strptime(match.group(0), '%m/%d/%Y')
                        except ValueError:
                            pass
            
            return None

    def _validate_values(self, values: Dict[str, Any], model_type: str) -> Dict[str, Any]:
            """
            Validate and clean extracted values
            
            Args:
                values (Dict[str, Any]): Extracted values
                model_type (str): Type of model
            
            Returns:
                Dict[str, Any]: Validated and cleaned values
            """
            validated = values.copy()
            
            # Ensure title is present
            if 'title' not in validated:
                validated['title'] = 'Untitled ' + model_type
            
            # Truncate fields
            validated['title'] = validated['title'][:100]
            
            if 'description' in validated:
                validated['description'] = validated['description'][:500]
            
            return validated

    #date calculation
    def _calculate_relative_time(num: int, unit: str) -> datetime:
        now = datetime.now()
        if unit == 'hour':
            return now + timedelta(hours=num)
        elif unit == 'day':
            return now + timedelta(days=num)
        elif unit == 'week':
            return now + timedelta(weeks=num)
        elif unit == 'month':
            return now + timedelta(days=30*num)
        return now

    def _parse_relative_date(relative_term: str) -> datetime:
        now = datetime.now()
        if relative_term == 'today':
            return now
        elif relative_term == 'tomorrow':
            return now + timedelta(days=1)
        elif relative_term == 'next week':
            return now + timedelta(weeks=1)
        return now





