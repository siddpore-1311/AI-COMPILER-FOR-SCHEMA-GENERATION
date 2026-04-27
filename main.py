import os
from groq import Groq
import json

client = Groq(api_key="Enter the key")

def stage_1_intent(prompt):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Extract software features as JSON. Must be valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

def stage_2_schema(intent):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Create DB and API schema as JSON based on these features. Ensure type safety and cross-layer consistency."},
            {"role": "user", "content": str(intent)}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

if __name__ == "__main__":
    user_input = "Build a CRM with login and payments."
    try:
        intent_data = stage_1_intent(user_input)
        final_output = stage_2_schema(intent_data)
        print(json.dumps(final_output, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        
def stage_3_validation_repair(final_config):
    db_tables = set(final_config.get("database", {}).get("schema", {}).keys())
    api_modules = set(final_config.get("api", {}).get("schema", {}).keys())
    missing_in_api = db_tables - api_modules
    
    if missing_in_api:
        repair_prompt = f"Missing API endpoints for these DB tables: {list(missing_in_api)}. Repair this JSON and return full version: {json.dumps(final_config)}"
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a validator. Repair the JSON for consistency and return it."},
                {"role": "user", "content": repair_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    return final_config

if __name__ == "__main__":
    user_input = "Build a CRM with login and payments."
    try:
        intent_data = stage_1_intent(user_input)
        schema_data = stage_2_schema(intent_data)
        final_output = stage_3_validation_repair(schema_data)
        print(json.dumps(final_output, indent=2))
    except Exception as e:
        print(f"Error: {e}")
