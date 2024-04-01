import requests
from googleapiclient.discovery import build
import base64

# Load the Hugging Face model
model_url = "https://api-inference.huggingface.co/models/juliensimon/autotrain-food101-1471154053" # Replace with your own Hugging Face API key
headers = {"Authorization": "{API KEY HERE}"}
YOUTUBE_DATA_API = "{API KEY HERE}" # Replace with your own YouTube Data API key


# Function to perform inference on the image
def perform_inference(image_path):
    with open(image_path, "rb") as f:
        data = f.read()

    response = requests.post(model_url, headers=headers, data=data)
    result = response.json()
    return result

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
def process_image(image_path):
    result = perform_inference(image_path)
    youtube_query = result[0]['label'] + " recipe"
    youtube_urls = search_youtube_videos(youtube_query)

    return {'result': result[0]['label'], 'youtube_urls': youtube_urls}

# Function to search meal by name using The Meal DB API
def search_meal_by_name(meal_name):
    url = f"{mealdb_base_url}search.php?s={meal_name}"
    response = requests.get(url)
    data = response.json()
    return data['meals'] if 'meals' in data else None

# Function to get recipe details by meal ID
def get_recipe_details(meal_id):
    url = f"{mealdb_base_url}lookup.php?i={meal_id}"
    response = requests.get(url)
    data = response.json()
    return data['meals'][0] if 'meals' in data else None

# Function to display meal details
def display_meal_details(meal):
    print(f"\nMeal: {meal['strMeal']}")
    print(f"Category: {meal['strCategory']}")
    print(f"Area: {meal['strArea']}")
    print(f"Instructions: {meal['strInstructions']}")
    
    # Get recipe details by meal ID
    recipe_details = get_recipe_details(meal['idMeal'])
    if recipe_details:
        print("\nIngredients:")
        for i in range(1, 21):
            ingredient = recipe_details.get(f'strIngredient{i}')
            measure = recipe_details.get(f'strMeasure{i}')
            if ingredient and measure:
                print(f" - {ingredient}: {measure}")


# Main loop
while True:
    picture_path = input("\n\nEnter the path to an image (or 'exit' to quit): ")
    print('-' * 50)  # Print a line of dashes


    if picture_path.lower() == 'exit':
        print("Exiting the program.")
        break

    try:
        output = process_image(picture_path)
        print(f"- Food: {output['result']}")

        # Asking for user input
        yes_or_no = input("- Do you want a guide on how to prepare it? (yes or no): ")
        if yes_or_no.lower() == 'yes':
            print("- Here are the top 5 videos how to make it:")
            # Output embedded YouTube video URLs with numbering
            for i, url in enumerate(output['youtube_urls'], start=1):
                print(f"   {i}. {url}")
        else:
            print("Have a nice day!")
        print()

    except Exception as e:
        print(f"Error processing image: {str(e)}")


    yes_or_no = input("- Would you like a recipe for it? (yes or no): ")

    if yes_or_no.lower() == 'yes':
        # The Meal DB API Base URL
        mealdb_base_url = "https://www.themealdb.com/api/json/v1/1/"

        # Test with the recognized food name
        meals = search_meal_by_name(output['result'])
        if meals:
            print(f"\nMeals found for '{output['result']}':")
            for i, meal in enumerate(meals, start=1):
                print(f"{i}. {meal['strMeal']}")

            # Ask the user to choose a meal
            while True:
                try:
                    choice = int(input("\nEnter the number of the meal you want to learn more about: "))
                    selected_meal = meals[choice - 1]
                    display_meal_details(selected_meal)
                    break
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
        else:
            print(f"No meals found for '{output['result']}'.")
