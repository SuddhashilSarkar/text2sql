import os
import json
from google import genai
from google.protobuf.json_format import MessageToJson # updated library import

def recognize_protocol(original_query: str) -> dict:
    """
    Recognizes the correct protocol for a user query, improves the query, and returns a JSON response.

    Args:
        original_query (str): The natural language input from the user.

    Returns:
        dict: JSON containing protocol code, original_query, and improved_query.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-pro"  # Using a valid model name


    protocol_table = """
# Text-to-SQL Protocol Classification

| Category            | Protocol Code | Description                          | Function                                      |
|---------------------|---------------|--------------------------------------|-----------------------------------------------|
| **Error**           | 00            | Invalid or unsupported request       | Error handling and feedback                   |
| **Query**           | 10            | Simple Query                         | Basic data retrieval                          |
| **Query & Display** | 11            | Table Display                        | Formatted tabular presentation                |
| **Query & Display** | 12            | Static Chart                         | Predefined charts (bar, line, pie, scatter)   |
| **Query & Display** | 13            | Dynamic Chart                        | Time-series visualizations                    |
| **Data Manipulation** | 20          | General DML                          | Generic data modification                     |
| **Data Manipulation** | 21          | Insert Data                          | Add new records with parameters               |
| **Data Manipulation** | 22          | Update Data                         | Modify records with conditions                |
| **Data Manipulation** | 23          | Delete Data                         | Remove records based on conditions            |
| **Data Definition** | 30            | General DDL                          | Generic schema modification                   |
| **Data Definition** | 31            | Create Table                         | Schema creation                               |
| **Data Definition** | 32          | Alter Table                          | Schema modification                           |
| **Data Definition** | 33            | Drop Table                           | Schema removal                                |
| **Data Definition** | 34            | Truncate Table                       | Data purging while preserving structure       |
| **Metadata**        | 40            | General Metadata                     | Schema information operations                |
| **Metadata**        | 41            | List Tables                          | Retrieve available tables                     |
| **Metadata**        | 42            | Describe Table                       | Retrieve table structure details              |
"""

    user_prompt = original_query

    # Define the function declaration for structured output
    function_declarations = [
        {
            "name": "recognize_protocol_output",
            "description": "Recognizes protocol and improves query",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "protocol": {
                        "type": "NUMBER",
                        "description": "Protocol code"
                    },
                    "original_query": {
                        "type": "STRING",
                        "description": "The original user query"
                    },
                    "improved_query": {
                        "type": "STRING",
                        "description": "The improved query"
                    }
                },
                "required": ["protocol", "original_query", "improved_query"]
            }
        }
    ]

    generate_content_config = {  # No longer a direct class instantiation
        "tools": [{"function_declarations": function_declarations}],
        "temperature": 0.0 # set the temperature to 0.0
    }

    system_instruction = f"""You are an intelligent protocol classifier and query enhancer.

**Available Protocols:**
{protocol_table}

Analyze the query and:

1. Identify the correct protocol code
2. Improve the query for clarity
3. Return JSON response

**Response Requirements:**
- Use valid JSON format and MUST CALL the function `recognize_protocol_output`
- Include protocol code, original_query, and improved_query
- Improved query should maintain original intent while adding specificity
- Never invent parameters that weren't in the original query

"""

    contents = [
        {
            "role": "user",
            "parts": [
                {
                    "text": f"{system_instruction}\nUser Query: {user_prompt}"
                }
            ]
        }
    ]

    model_instance = genai.GenerativeModel(model_name=model) # use GenerativeModel

    response = model_instance.generate_content(
        contents=contents,
        generation_config = generate_content_config,
        stream=False,  # Set stream to False
    )

    try:
        # Extract the function call arguments from the response
        function_call = response.candidates[0].content.parts[0].function_call
        arguments_str = MessageToJson(function_call.args)
        return json.loads(arguments_str)
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        raise ValueError(f"Failed to decode JSON from LLM or extract function call: {e}. Raw Response: {response.text}")
    except Exception as e:
        raise ValueError(f"LLM processing error: {e}")

# -------------------------------------------------
# Example usage
# -------------------------------------------------
if __name__ == "__main__":
    query = "What is the total revenue this month?"
    result = recognize_protocol(query)
    print(json.dumps(result, indent=2))