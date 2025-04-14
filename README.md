# MysticAIl Fortune Teller

UNDER DEVELOPMENT

## Description
Simple project for a Fortune Teller, which generates random cards and predicts your future with AI.

It retrieves a card name from a random pool of adjectives and subjects (and also some pre-defined golden cards) and then simply throws the *guess my personality, my future, my best dreams and my worst fears by interpreting the meaning of this card* prompt to an AI text generation (default model is set to `openai` but can be easily changed in the code, while the default image generation model is `flux`).

At each step the user can either change the card image, customize it with a specific prompt, ask more info about the current interpretation or skip to the next one.
If the user wants to stop, the fortune teller will give a summary interpretation of the picked cards and saves everything in a pdf file.


## Installation

Setup a virtual environment and install the required dependencies (windows: replace source venv/bin/activate with simply .venv/Scripts/activate):

```
pip3 install venv
python3 -m venv venv
source venv/bin/activate
pip3 install -e .
```

OR use the requirements.txt file (`pip3 install -r requirements.txt`)


## Usage

Just launch the entry point with:

```
fortune_teller-cli
```


## Code
The code is launched with `main.py`, this handles the initial interaction with the user (starting questions) and creates a **Fortune_Teller** object.
- `ai_utils.py` contains the **Fortune_Teller** class and some functions to interact with AI servers (thanks to the [Pollinations](https://pollinations.ai/) modules)
- `pdf_utils.py` handles the pdf generation


## Customization
The txt files can be customized (except for vocabulary.txt) to change the card pool, you can either change or delete values or also add copies to raise probabilities of certain adjectives/subjects/golden cards.
The card images are stored as png files in a `generated_images` folder, while the predictions and summaries are stored in pdf files in a `generated_predictions` folder.

The possible languages are Italian and English, but it can be easily extended to other languages adding a folder with subjects, adjectives and standard phrases ( these ones in the `vocabulary.txt` file)
The personal information can also be changed (default: age, name, lucky number and favourite color)
