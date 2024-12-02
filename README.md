# Local Voice Assistant

This project is a local voice assistant that operates offline, entirely independent of an internet connection. It uses pre-downloaded models to provide features like speech recognition, conversational AI, and text-to-speech synthesis.
Key Features:

- **Offline Speech Recognition:** Transcribes audio input to text using a local Whisper model.
- **AI Chat Engine:** Processes user input and generates responses via the Ollama model.
- **Text-to-Speech Synthesis:** Converts AI-generated responses to spoken audio using Piper voice models.
- **Silence Detection:** Automatically detects when the user stops speaking and processes the input.
- **Exit Command:** You can exit the conversation by saying “bye.”

### Functionality:

The assistant listens for audio input, transcribes it into text, processes it using the AI chat model, and responds with synthesized speech. It provides a seamless and private interaction entirely on your local machine.

This assistant is ideal for those who value privacy, need an offline solution, or want to experiment with AI technologies locally.


### Installation Process

Follow these steps to set up and run the local voice assistant:
Prerequisites

- Python 3.11 is required.
    Ensure Python is installed by running:
    
    ```commandline
    python --version
    ```
    If not, download and install Python 3.11.* (pyenv...).

- **Step 1:** Clone the Repository

    Clone the project repository to your local machine:
    ```commandline
    git clone https://github.com/tibssy/local-voice-assistant
    cd local-voice-assistant
    ```

- **Step 2:** Create a Virtual Environment

    Use a virtual environment to manage dependencies. Create and activate it:
    ```commandline
    python -m venv venv
    source venv/bin/activate
    ```

- **Step 3:** Install Dependencies

    Install the required Python packages listed in requirements.txt:
    ```commandline
    pip install -r requirements.txt
    ```

  - **Step 4:** Download and Configure the TTS Model

    Before running the assistant, ensure you have downloaded the selected TTS model for Piper.
    You can download the models from [Piper Samples](https://rhasspy.github.io/piper-samples/).
  
    After downloading, add the model path to the PIPER_MODEL_PATH constant in the code or place the model file in the project directory.


  ![swappy-20241202_035951](https://github.com/user-attachments/assets/5e211cf0-1031-480c-8c9a-6d0612241056)

- **Step 5:** Verify Installation

    Make sure all dependencies are installed correctly without any errors. Pay special attention to the installation of Piper TTS, as it supports Python 3.11 but not Python 3.12.


- **Step 6:** Run the Assistant

    Start the voice assistant:
    ```commandline
    python main.py
    ```
    The assistant will begin listening for audio input. You can exit the assistant by saying “bye.”

### Important Notes:

Ensure Python 3.11: If another Python version is the default on your system, specify python3.11 explicitly during steps like creating the virtual environment.
SoundDevice Privileges: If you encounter issues with sounddevice or audio input/output, ensure your system audio is properly configured. You may need elevated privileges or adjustments for your environment (e.g., Wayland, PulseAudio).