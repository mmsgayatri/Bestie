import speech_recognition as sr
import pyttsx3
import requests
from googletrans import Translator


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def fallback_response(prompt):
    """Fallback function when API is unavailable"""
    common_responses = {
        "hello": "Hello! How can I help you today?",
        "how are you": "I'm functioning well, thank you for asking!",
        "time": "I'm sorry, I can't check the time right now.",
        "help": "I can help with basic tasks like weather information and translation.",
        "name": "I'm your voice assistant. You can call me Bestie!"
    }

    # Check for keywords in prompt
    for key, response in common_responses.items():
        if key in prompt.lower():
            return response

    return "I'm currently operating in offline mode due to API limitations. I can help with weather information and basic tasks."


def try_genai_response(prompt):
    """Try to use Gemini API with error handling"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=" AIzaSyCAcUVxql6Kn20xmgHT-8pgBw9mWrs5jIM")  # Replace with your actual API key

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 500,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[])
        convo.send_message(prompt)

        return convo.last.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return fallback_response(prompt)


def translate(text, target_language='en'):
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest=target_language).text
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails


def weather(city_name):
    API_Key = '2ad189e85c6980a11a12747acd9dfa58'  # Consider using environment variables for API keys
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_Key}&units=metric'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            store = response.json()
            weather_update = f"Weather update in {city_name} is {store['weather'][0]['description']}. " \
                             f"Humidity: {store['main']['humidity']}%, " \
                             f"Temperature: {store['main']['temp']}°C, " \
                             f"Feels like: {store['main']['feels_like']}°C."
            return weather_update
        else:
            return f"Sorry, couldn't fetch weather information. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching weather data: {e}"


def main():
    recognizer = sr.Recognizer()
    target_language = 'en'  # Initialize target_language here
    offline_mode = False  # Track if we're in offline mode

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                audio = recognizer.listen(source)
                print("Recognizing...")
                command = recognizer.recognize_google(audio)
                print("You said:", command)

                if "bestie" in command.lower():
                    speak("Hey there! How can I help you today?")

                elif "exit" in command.lower() or "stop" in command.lower():
                    speak("Goodbye!")
                    break

                elif "climate" in command.lower() or "weather" in command.lower():
                    speak("Tell me the city you want to know about weather conditions.")
                    audio = recognizer.listen(source)
                    city = recognizer.recognize_google(audio)
                    print("City:", city)
                    weather_info = weather(city)
                    speak(weather_info)

                elif "translate" in command.lower():
                    speak("What language would you like the responses to be translated into?")
                    audio = recognizer.listen(source)
                    target_language = recognizer.recognize_google(audio)
                    print("Target Language:", target_language)
                    speak("Language set to " + target_language)
                    print("Translate command recognized")

                elif "offline mode" in command.lower():
                    offline_mode = not offline_mode
                    status = "enabled" if offline_mode else "disabled"
                    speak(f"Offline mode {status}")
                    print(f"Offline mode {status}")

                else:
                    if offline_mode:
                        response = fallback_response(command)
                    else:
                        response = try_genai_response(command)

                    print("Response:", response)

                    if target_language != 'en':  # Check if translation is needed
                        translated_response = translate(response, target_language)
                        print("Translated Response:", translated_response)
                        speak(translated_response)
                    else:
                        speak(response)

            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
                speak("Sorry, something went wrong. Please try again.")


if __name__ == "__main__":
    main()
