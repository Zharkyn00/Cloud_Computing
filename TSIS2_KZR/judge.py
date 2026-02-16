# pip install google-genai

import os
import json
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("AIzaSyC-YXqzvnXUFActdxJH2zRZpmiDRnlQC_s"),
    )

    model = "gemini-3-flash-preview"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""
PRD:
Write a Python function to parse a CSV file.
It must:
- Handle FileNotFoundError
- Return a list of dictionaries.

CODE:
import csv

def parse_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)
"""),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        system_instruction="""
You are a strict QA Judge Agent.

Return ONLY valid JSON in this exact structure:

{
  "compliance_score": 0-100,
  "status": "PASS/FAIL",
  "audit_log": [
    {
      "requirement": "string",
      "met": true/false,
      "comment": "string"
    }
  ],
  "security_check": "Safe/Unsafe"
}

DO NOT add explanations.
DO NOT add text before or after JSON.
""",
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    # Сохраняем в файл
    with open("compliance_report.json", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("✅ Report saved to compliance_report.json")


if __name__ == "__main__":
    generate()
