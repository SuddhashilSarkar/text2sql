import os
import yaml
from google import genai
from google.genai import types

def load_schema(schema_path="schema.yaml"):
    """Loads the database schema from a YAML file."""
    with open(schema_path, "r") as file:
        return yaml.safe_load(file)

def generate_sql_query(user_input, schema):
    """Generates an SQL query using Gemini based on user input and schema."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-flash"

    schema_text = yaml.dump(schema, default_flow_style=False)  # Convert schema to YAML string

    system_instructions = types.Part.from_text(text=f"""You are an expert SQL generator. Your task is to generate a valid SQLite SQL query based on the given database schema and user request. Ensure the query adheres to SQLite syntax.

### Database Schema:
{schema_text}

### Instructions:
- Use only the tables and columns provided in the schema.
- Ensure that all constraints (e.g., NOT NULL, UNIQUE, PRIMARY KEY) are respected.
- Use proper WHERE conditions for filtering data based on user input.
- Do not include table names or columns that are not present in the schema.
- If a column has a UNIQUE constraint (e.g., email, phone), use it to filter queries when applicable.
- If a request is ambiguous, make an educated assumption based on common use cases.

### Output:
Provide only the SQL query in JSON format.
""")

    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_input)]),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            properties={
                "query": genai.types.Schema(type=genai.types.Type.STRING),
                "response": genai.types.Schema(type=genai.types.Type.STRING),
            },
        ),
        system_instruction=[system_instructions],
    )

    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )

    return response.text  # Returning generated SQL query in JSON format

if __name__ == "__main__":
    schema = load_schema("schema.yaml")  # Load schema from file
    user_query = input("Enter your query: ")  # User input
    sql_query = generate_sql_query(user_query, schema)
    print("\nGenerated SQL Query:\n", sql_query)
