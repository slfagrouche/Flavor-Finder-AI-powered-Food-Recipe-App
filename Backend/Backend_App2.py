from openai import OpenAI
import requests
from googleapiclient.discovery import build
import base64


YOUTUBE_DATA_API = "{API KEY HERE}" # Replace with your own YouTube Data API key
api_key = "{API KEY HERE}"
client = OpenAI(api_key=api_key)



response = client.chat.completions.create(
  model="gpt-4-vision-preview",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", 
        "text": 
        """Instructions:

1. Analyze the provided image or list of ingredients.
2. Generate possible dishes based on the context.
4. If ingredients are provided separately, suggest dishes that can be made using those ingredients.
Output Format:
- Provide the list of possible dishes.
- For each dish, include a brief description or recipe.
- Use bullet points or paragraphs for readability."""},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://www.marthastewart.com/thmb/ovphRAVK5PkUG73tEVcxw7ZAeWo=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/978784-one-pan-pasta-step_01-9d35ed5c6db64097b753707431da40f4.jpg",
          },
        },
      ],
    }
  ],
  max_tokens=700,
)

print("\n\n")
print(response.choices[0].message.content)

print("-" * 50)
user_choice = input("Enter the name of the desired dish from one of the following dishes above: ")

# Function to search YouTube videos based on a query
def search_youtube_videos(query):
    api_key =  YOUTUBE_DATA_API 
    youtube = build('youtube', 'v3', developerKey=api_key)

    search_params = {
        'q': query,
        'part': 'snippet',
        'maxResults': 5,  # Number of videos to retrieve
        'type': 'video',
    }

    search_response = youtube.search().list(**search_params).execute()
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    embedded_urls = [f"https://www.youtube.com/embed/{video_id}" for video_id in video_ids]

    return embedded_urls

# Function to handle the overall process
def process_image(user_choice):
    youtube_query = user_choice + " recipe"
    youtube_urls = search_youtube_videos(youtube_query)
    return {'result': user_choice, 'youtube_urls': youtube_urls}

# Process the user's choice
output = process_image(user_choice)

# Asking if the user wants a video guide
print("-" * 50)
yes_or_no = input("- Do you want a video guide on how to prepare it? (yes or no): ")
if yes_or_no.lower() == 'yes':
    print("\n- Here are the top 5 videos on how to make it:")
    # Output embedded YouTube video URLs with numbering
    for i, url in enumerate(output['youtube_urls'], start=1):
        print(f"   {i}. {url}")
    print()

# Asking if the user wants a recipe
print("-" * 50)
yes_or_no = input("- Would you like a recipe for it? (yes or no): ")
if yes_or_no.lower() == 'yes':
    completion = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": f"I would like a strong recipe for making {output['result']}. Please provide step-by-step instructions."}])
    print("\n- Recipe:")
    print("-" * 50)  # Add dashes for separation
    print(completion.choices[0].message.content.strip())  # Print the recipe
    print("-" * 50)  # Add dashes for separation

# Asking if the user wants an AI assistant for the recipe
print("-" * 50) # Add dashes for separation
yes_or_no = input("- Do you want an AI assistant on how to make it? (yes or no): ")
if yes_or_no.lower() == 'yes':
    print("\n- Your Chef AI assistant is ready! How can I help you?")
    print("-" * 50)  # Add dashes for separation
    messages = [{"role": "system", "content": f"AI assistant for making {output['result']}\n"}]
    while True:
        message = input()
        if message.lower() == "quit()":
            break
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages)
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print("\n" + reply + "\n")
    print("-" * 50)  # Add dashes for separation
