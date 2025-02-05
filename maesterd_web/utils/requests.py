from openai import OpenAI, OpenAIError
import requests.exceptions


def make_openai_request(prompt, api_key):
    # return 'that is the fake api response'
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to a valid model name
            messages=[
                {"role": "system", "content": "You are a dungeons and dragons role play game master"},
                {"role": "user", "content": prompt}
            ],
            timeout=30  # Add a timeout to prevent hanging
        )
        return completion.choices[0].message.content
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.RequestException("Connection error. Please check your internet connection")
    except OpenAIError as openai_error:
        if "invalid_api_key" in str(openai_error).lower():
            raise RuntimeError('Invalid OpenAI API key. Please check your API key and try again')
        elif "rate_limit" in str(openai_error).lower():
            raise RuntimeError('Rate limit exceeded. Please wait a moment before trying again')
        else:
            raise RuntimeError('OpenAI API error: ' + str(openai_error))
    except Exception as e:
        raise Exception(f"Unexpected error in OpenAI request: {str(e)}")
