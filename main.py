import os
import google.generativeai as genai
import time

def main():
    # Ensure your Google API key is set as an environment variable
    # Example: export GOOGLE_API_KEY="YOUR_API_KEY"
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set it before running the script.")
        return

    genai.configure(api_key=api_key)

    # --- IMPORTANT: Replace this with the path to your local video file ---
    # Make sure the video is relatively short (e.g., a few minutes) for quicker
    # processing and to stay within typical free tier limits.
    video_file_path = "path/to/your/video.mp4" # <<< UPDATE THIS LINE

    if not os.path.exists(video_file_path):
        print(f"Error: Video file not found at '{video_file_path}'.")
        print("Please update 'video_file_path' with the correct path to your video.")
        return

    print(f"Uploading video file: {video_file_path}...")
    video_file = None # Initialize to None for finally block
    try:
        # Upload the video file to Google's infrastructure for analysis.
        # This is a prerequisite for Gemini's video understanding capabilities.
        video_file = genai.upload_file(path=video_file_path, display_name="Agentic Video Demo")
        print(f"Video uploaded. File ID: {video_file.name}")

        # Wait for the file to be processed by Google's services.
        # Gemini can only analyze files that are in a 'READY' state.
        print("Waiting for video file to be processed...")
        while video_file.state.name == "PROCESSING":
            time.sleep(10) # Wait for 10 seconds before checking again
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            print(f"Error: Video file processing failed. Reason: {video_file.error_message}")
            return

        print("Video file ready for analysis.")

        # Initialize the Gemini model that supports video input (e.g., gemini-1.5-flash).
        model = genai.GenerativeModel("gemini-1.5-flash")

        # --- Craft an "agentic" prompt to demonstrate decision-making ---
        # This prompt asks the model to go beyond simple summarization and
        # suggest specific actions based on the video content, simulating
        # an autonomous agent's behavior.
        prompt = (
            "Analyze the provided video. Identify the main activity or event. "
            "If you detect any unusual, critical, or potentially dangerous situations, "
            "describe the situation in detail and suggest an immediate, specific action "
            "that a human or an automated system should take. "
            "If the video shows a normal, non-critical activity, provide a concise summary "
            "of what is happening and suggest a relevant follow-up question a user might ask."
        )
        
        print("\nSending video and agentic prompt to Gemini model...")
        # Pass both the text prompt and the uploaded video file to the model.
        response = model.generate_content([prompt, video_file]) 

        print("\n--- Gemini Agentic Video Analysis Result ---")
        print(response.text)
        print("------------------------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up: Delete the uploaded file to free up resources and storage.
        # This is important for managing API usage and costs.
        if video_file and video_file.state.name != "FAILED":
            print(f"\nDeleting uploaded file: {video_file.name}...")
            genai.delete_file(video_file.name)
            print("File deleted.")

if __name__ == "__main__":
    main()
