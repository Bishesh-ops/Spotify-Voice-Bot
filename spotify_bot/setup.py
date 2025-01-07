from setuptools import setup, find_packages

setup(
    name="spotify_bot",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "spotipy",
        "python-dotenv",
        "SpeechRecognition"
    ],
    entry_points={
        "console_scripts": [
            "spotify-bot=spotify_bot.bot_core:main"
        ],
    },
)
