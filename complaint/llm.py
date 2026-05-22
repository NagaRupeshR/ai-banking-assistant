import json
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_analysis(prompt):
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        temperature=0.2,
        response_format={'type': 'json_object'},
        messages=[
            {
                'role': 'system',
                'content': 'You are an expert Indian banking complaint resolution assistant.',
            },
            {'role': 'user', 'content': prompt},
        ],
    )

    content = response.choices[0].message.content
    return json.loads(content)