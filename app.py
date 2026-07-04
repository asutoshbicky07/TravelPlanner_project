import gradio as gr
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================
# ENTER YOUR GEOAPIFY API KEY
# ==========================
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


# Get coordinates of the city
# Get coordinates of the city
def get_coordinates(city):
    url = f"https://api.geoapify.com/v1/geocode/search?text={city}&format=json&apiKey={GEOAPIFY_API_KEY}"

    print("URL:", url)

    response = requests.get(url)

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    data = response.json()

    if data.get("results"):
        lat = data["results"][0]["lat"]
        lon = data["results"][0]["lon"]
        return lat, lon

    return None, None


# Fetch nearby places
def get_places(lat, lon, category, limit=5):
    url = f"https://api.geoapify.com/v2/places?categories={category}&filter=circle:{lon},{lat},5000&limit={limit}&apiKey={GEOAPIFY_API_KEY}"
    response = requests.get(url).json()

    places = []

    if response.get("features"):
        for place in response["features"]:
            places.append(
                {
                    "name": place["properties"].get("name", "Unknown"),
                    "address": place["properties"].get(
                        "address_line1",
                        "Address Not Available",
                    ),
                }
            )

    return places


def generate_plan(location, days, budget, travellers):

    lat, lon = get_coordinates(location)

    if lat is None:
        return "❌ City not found."

    attractions = get_places(lat, lon, "tourism.attraction", 5)
    restaurants = get_places(lat, lon, "catering.restaurant", 5)
    hotels = get_places(lat, lon, "accommodation.hotel", 3)

    output = f"# 🌍 Travel Plan for {location}\n\n"

    for day in range(1, int(days) + 1):

        output += f"## Day {day}\n\n"

        if attractions:
            place = attractions[(day - 1) % len(attractions)]
            output += f"🏛 Attraction : **{place['name']}**\n"
            output += f"📍 {place['address']}\n\n"

        if restaurants:
            food = restaurants[(day - 1) % len(restaurants)]
            output += f"🍴 Restaurant : **{food['name']}**\n"
            output += f"📍 {food['address']}\n\n"

    output += "## 💰 Budget Estimate\n\n"
    output += f"Budget : ₹{budget}\n\n"

    output += "Accommodation : ₹1000 - ₹4000/night\n"
    output += "Food : ₹500 - ₹1500/day\n"
    output += "Transport : ₹300 - ₹1000/day\n\n"

    output += "## 🏨 Recommended Hotels\n\n"

    for hotel in hotels:
        output += f"• {hotel['name']} - {hotel['address']}\n"

    return output


with gr.Blocks() as demo:

    gr.Markdown("# ✈ AI Travel Planner")

    location = gr.Textbox(label="Destination")

    days = gr.Slider(1, 14, value=2, label="Days")

    budget = gr.Number(label="Budget (INR)", value=10000)

    travellers = gr.Dropdown(
        [1, 2, 3, 4, 5, 6],
        value=2,
        label="Travellers",
    )

    button = gr.Button("Generate Travel Plan")

    output = gr.Markdown()

    button.click(
        generate_plan,
        inputs=[location, days, budget, travellers],
        outputs=output,
    )


demo.launch()