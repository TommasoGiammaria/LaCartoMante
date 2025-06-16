import os
import random
import time
from datetime import datetime

import pollinations
from PIL import Image

"""
This module contains the functions to interact with the Pollinations API.
The fortune teller class handles the card generation picking a random card from a pool names and adjectives.
The "golden cards" are also available, these are pre-defined cards with a specific name and adjective.
It can also generate a text prompt for the user to interpret the card image or to change the card image.
"""



def generate_ai_text(
    string_prompt : str = "",
    system_string : str = "You are a fortune teller reading cards for me",
    ai_model : pollinations.Model = pollinations.Text.openai(),
    img_path : str = "",
    prev_messages : list = []
):
    """
    function to generate text from single string prompt.
    default model is openai, but it can be changed to pollinations or other models.
    NB: the image is not used in the prompt, but it can be added to the model to generate a reply.
    """
    text_model = pollinations.Text(
        model=ai_model, system=system_string, messages=[], contextual=True
    )
    if img_path != "":
        text_model.image(file = img_path)

    response = text_model(
        prompt=string_prompt, messages = prev_messages, encode=True
    )
    response_string = str(response.response)
    # format the reply to add \n characters after dots
    reply = ""
    for line in response_string.split("\n"):
        reply += "\n" + ".\n".join(line.split(". "))
    replydict = { "model" : text_model, "reply" : reply}
    return replydict


def generate_ai_reply(text_model, string_prompt : str = ""):
    """
    function to interact with multiple prompts, generating a text reply at each step.
    """
    response = text_model(prompt=string_prompt, encode=True)
    response_string = str(response.response)
    # format the reply to add \n characters after dots
    reply = ""
    for line in response_string.split("\n"):
        reply += "\n" + ".\n".join(line.split(". "))
    return reply


def generate_ai_image(prompt :str = "", show : bool = False, save_path : str = "generated_images"):
    """
    function to generate images from single string prompt (similar to text generator)
    NB: can be shown only if it is locally saved!
    """
    image_model = pollinations.Image(
        model = pollinations.Image.flux(),
        seed = "random",
        width = 514,
        height = 1024,
        enhance = True,
        nologo = True,
    )
    image = image_model(prompt)
    # saving is necessary to access the image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # get time stamp
    image_save_name = f"img_{timestamp}.png"  # name the image and define its path
    image_save_path = os.path.join(save_path, image_save_name)
    os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
    image.save(image_save_path)
    if show:
        image = Image.open(
            image_save_path
        )  # Crop watermark/artifacts (adjust as needed)
        image = image.crop((0, 0, image.width, image.height))
        image.show()
    replydict = { "model" : image_model, "path" : image_save_path, "reply" : image}
    return replydict


def generate_ai_image_reply(
        img_model,
        string_prompt : str = "",
        show = False,
        save_path : str = "generated_images",
        language : str = "English"):
    """
    function to interact with multiple prompts (generating a new image starting from the previous at each step)
    """
    image = None
    if language == "English":
        image = img_model(
            prompt = f"Change the previous image with the following instructions: {string_prompt}. Keep the same fortune teller card format and the same card title, as well as the image style."
            )
    elif language == "Italiano":
        image = img_model(
            prompt = f"Cambia questa immagine con le seguenti istruzioni: {string_prompt}. Mantieni lo stesso formato di carta dei tarocchi e lo stesso titolo della carta, così come lo stile con cui hai generato la prima carta."
            )
    # saving is necessary to access the image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    # get time stamp
    image_save_name = f"img_{timestamp}.png"    # name the image and define its path
    image_save_path = os.path.join(save_path, image_save_name)
    os.makedirs(os.path.dirname(image_save_path), exist_ok = True)
    image.save(image_save_path)
    if show:           
            image = Image.open(
                image_save_path
            )   # Crop watermark/artifacts (adjust as needed)
            image = image.crop((0, 0, image.width, image.height))
            image.show()
    replydict = { "path" : image_save_path, "reply" : image}
    return replydict


class Fortune_Teller:
    """
    The Fortune Teller class handles all the predictions and interactions with the user.
    It is able to generate a random card, show the card image,
    generate a text prompt for the user to change the card image or explain interpretations,
    and it keeps track of the generated cards to make a summary description of them at the end.
    All the predictions are stored in a pdf file.
    The possible languages are Italian and English, but it can be easily extended to other languages.
    """

    languages_list = ["Italiano", "English"]

    def __init__(self, datapath = "English", savepath = "generated_images"):
        self.error = False
        self.username = "User"
        self.text_model = pollinations.Text()
        self.image_model = pollinations.Image()
        self.savepath = savepath
        self.seed = random.randint(0, 1000000)
        self.language = os.path.split(datapath)[1]
        if self.language not in self.languages_list:
            print("ERROR - Language not recognized!")
        self.subjects = []
        self.adjectives = []
        self.cardpool = []
        self.prev_msgs = []
        self.standard_phrases_dict = {}
        self.current_card = ""
        # we set a default card if somehow a card is not picked before the first profecy
        if self.language == "English":
            self.current_card = "The crazy panda"
        elif self.language == "Italiano":
            self.current_card = "Il tasso ninja"
        self.card_title_history = []
        if os.path.isdir(datapath):
            if len(os.listdir(datapath)) == 4:
                try:
                    with open(os.path.join(datapath, "subjects.txt")) as file:
                        self.subjects = file.read().split("\n")
                    with open(os.path.join(datapath, "adjectives.txt")) as file:
                        self.adjectives = file.read().split("\n")
                    with open(os.path.join(datapath, "golden_cards.txt")) as file:
                        self.cardpool = file.read().split("\n")
                    with open(os.path.join(datapath, "vocabulary.txt")) as file:
                        lines = file.read().split("\n")
                        for line in lines:
                            values = line.split(" = ")
                            dict_key = values[0]
                            dict_value = values[1]
                            if "-" in values[1]:
                                dict_value = values[1].split("-")
                            elif "+" in values[1]:
                                dict_value = "\n".join(values[1].split("+"))
                            self.standard_phrases_dict[dict_key] = dict_value
                except:
                    print("ERROR - error while opening the vocabulary files")
                    self.error = True
            else:
                print("ERROR - unexpected number of files in the selected language folder")
                self.error = True
        else:
            print("ERROR - the selected language folder does not exists!")
            self.error = True


    def pick_card(self) -> None:
        """
        we can either take a whole card name from the "golden cards" pool or randomly mixing the adj/subj pools
        """
        redo = True
        while redo:
            if random.randint(0, 1) == 0:
                selected_card = self.cardpool[random.randint(0, len(self.cardpool) - 1)]
                
                self.current_card = selected_card
                self.cardpool.remove(selected_card)
            else:
                single_subject = self.subjects[random.randint(0, len(self.subjects) - 1)]
                single_adj = self.adjectives[random.randint(0, len(self.adjectives) - 1)]

                self.subjects.remove(single_subject)
                self.adjectives.remove(single_adj)

                # first we select the proper construction depending on the language
                if self.language == "English":
                    self.current_card = f"The {single_adj} {single_subject}"
                if self.language == "Italiano":
                    articolo = single_subject.split(" ")[0]
                    if single_subject[:2] == "l'": articolo = "l'"
                    if single_adj[-1] == "*":
                        # print(single_adj)
                        single_adj = single_adj[:-1]
                        
                        # print(single_adj)
                        if single_subject[-1] == "o": single_adj += "o"
                        elif single_subject[-1] == "a":
                            if articolo in ["la", "La"]: single_adj += "a"
                            else: single_adj += "o"                    
                        elif single_subject[-1] == "e": 
                            if articolo in ["la", "La"]: single_adj += "a"
                            else: single_adj += "o"
                        
                        # print(single_adj)
                    self.current_card = f"{single_subject} {single_adj}"

            # this is done to avoid copies given that there are multiple adjectives and subjects (to manage card generation probabilities)
            if f'"{self.current_card}"' not in self.card_title_history:
                self.card_title_history.append(f'"{self.current_card}"')
                redo = False


    def hear_the_ancient_voices(
            self,
            person_dict = {
                "name" : "Tommaso",
                "age" : 32,
                "number" : 2,
                "color" : "green"
                }
    ) -> str:
        """
        We generate standard a text prompt string using the card name to interpret the card with AI
        """
        self.username = person_dict["name"]
        text_prompt = ""
        if self.language == "English":
            text_prompt = f'You picked a card named "{self.current_card}" from a fortune teller card deck. You have to guess my personality, my future, my best dreams and my worst fears by interpreting the meaning of this card.'
            text_prompt += f"Here are small hints about me: my name is {person_dict['name']}, I am {person_dict['age']} years old, my lucky number is {person_dict['number']} and my favourite color is {person_dict['color']}. Take these into account."
        if self.language == 'Italiano':
            text_prompt = f'Hai appena pescato una carta intitolata "{self.current_card}" da un mazzo di tarocchi. Interpreta i segni il significato mistico di questa carta per indovinare la mia personalità, il mio futuro, i miei sogni e le mie paure. Tieni conto di queste informazioni.'
            text_prompt += f"Ecco alcune informazioni su di me: mi chiamo {person_dict['name']}, ho {person_dict['age']} anni, il mio numero fortunato è {person_dict['number']} e il mio colore preferito è {person_dict['color']}."
        # add languages here 

        # we generate the reply of the fortune teller (so the user can begin reading while waiting the image to be generated)
        # _, profecy = generate_ai_text(text_prompt, self.standard_phrases_dict["system"], card_image_path) # this adds also the image to the prompt (honestly I don't know if it's better or worse)
        replydict = generate_ai_text(text_prompt, self.standard_phrases_dict["system"])
        profecy = replydict["reply"]

        self.prev_msgs.append(pollinations.Text.Message( role = self.standard_phrases_dict["referrer"], content = profecy))
        
        return profecy


    def punish_insolence(self, user_prompt = "") -> str:
        """
        If the user replies something else than "yes" or "no", the fortune teller will get angry and will reply with an evil message (currently under development)
        NOTE: the fortune teller will not stop until the user yells SHUT UP! (ZITTO! in Italian)
        """
        # the only way to stop the fortune teller is to yell SHUT UP!
        exit_strings = [
            "SHUT UP\n",
            "SHUT UP",
            "Zitto",
            "Stai zitto",
            "Zitta",
            "Stai zitta",
            "Zitto!",
            "ZITTO",
            "Zitta!",
            "ZITTA",
            "STAI ZITTO",
            "STAI ZITTA",
            "SMETTILA",
            "smettila",
            "Smettila",
            "zitto",
            "Shutp up\n",
            "Shut up",
            "Shut up!",
            "Shut up!!",
            "shut up",
            "shut up!",
            "shut up!!"]
        
        # now the fortune teller is pissed        
        replydict = generate_ai_text(
            user_prompt,
            self.standard_phrases_dict["system"],
            pollinations.Text.evil(),
            prev_messages = self.prev_msgs
        )
        self.text_model = replydict["model"]
        evil_reply = replydict["reply"]

        # enter conversation loop
        while True:
            print(f"\n{self.standard_phrases_dict["referrer"]}: {evil_reply}")
            loop_user_reply = input(f"\n{self.username}: ")
            if loop_user_reply in exit_strings:
                print("\n")
                print(f"{self.standard_phrases_dict['referrer']}: ok...      ", end = "\r")
                time.sleep(1)
                if self.language == "English": print("Fortune teller: ok... rude")
                elif self.language == "Italiano":print("Cartomante: ok... maleducato")
                time.sleep(2)
                string_to_print = f"{self.standard_phrases_dict['referrer']}: "
                string_to_print_add = "now LEAVE ME ALONE. BYE!\n"
                if self.language == "Italiano": string_to_print_add = "ora LASCIAMI IN PACE. CIAO!\n"
                for char in string_to_print_add:
                    string_to_print += char
                    print(string_to_print + "                 ", end = "\r")
                    time.sleep(0.3)
                return evil_reply
            else:
                evil_reply = generate_ai_reply(self.text_model, loop_user_reply)


    def look_at_the_crystall_ball(self, show_image = False, new_input = "") -> Image:
        """
        We generate a text prompt string using the card name to generate the card image with AI
        """
        # INPUT = {focus}
        # OUTPUT = {description} \n ![IMG](https://image.pollinations.ai/prompt/{description})
        # {description} = {focusDetailed},%20{adjective1},%20{adjective2},%20{visualStyle1},%20{visualStyle2},%20{visualStyle3},%20{artistReference} 
        # def get_personalized_string(title, inputstring):
        #     description = f'A fortune teller card of {inputstring} with the following title "{title}" at the bottom of the card,%20mystic%20epic,%20fortune teller card,%20Divination,%20Plain view'
        #     return f'INPUT = {inputstring}\n\nOUTPUT = {description} \n ![IMG](https://image.pollinations.ai/prompt/{description})'
        # first we select the proper construction depending on the language
        image_prompt = ""
        replydict = {}
        if new_input != "":
            image_prompt = new_input
            replydict = generate_ai_image_reply(
                self.image_model,
                image_prompt,
                show_image,
                self.savepath,
                self.language
            )
        else:
            if self.language == "English":
                card_image_description = f'Fortune teller card of {self.current_card}, title: "{self.current_card}" bold antique font at bottom of the card,%20mystic%20epic,%20fortune teller card,%20Divination,%202D",%20mysterious'
                image_prompt = f'INPUT = {self.current_card}\n\nOUTPUT = {card_image_description} \n ![IMG](https://image.pollinations.ai/prompt/{card_image_description})'
            if self.language == 'Italiano':
                card_image_description = f'Carta dei tarocchi che raffigura {self.current_card}. IL testo visibile nella carta è il titolo: "{self.current_card}", in grassetto nel bordo inferiore della carta, in italiano,%20mistico%20divinazione,%20tarocchi,%20cartomante,%202D,%20no prospettiva'
                image_prompt = f'INPUT = {self.current_card}\n\nOUTPUT = {card_image_description} \n ![IMG](https://image.pollinations.ai/prompt/{card_image_description})'
            # add languages here
            replydict = generate_ai_image(image_prompt, show_image, self.savepath)
            self.image_model = replydict["model"]
        
        current_card_image = replydict["reply"]
        return current_card_image


    def summarize_profecies(self) -> str:
        """
        At the end of the conversation the fortune teller will summarize the profecies,
        and ask the user if they want to ask anything else about these profecies.
        The user reply is given directly as argument to the AI to generate a reply.
        """
        text_prompt = ""
        all_cards = ", ".join(self.card_title_history)
        if self.language == "English":
            text_prompt = f'You picked {len(self.card_title_history)} fortune teller cards with the following names: {all_cards}. Summarize the meaning of this combination of cards.'
        if self.language == "Italiano":
            text_prompt = f'Hai appena pescato {len(self.card_title_history)} carte dal mazzo dei tarocchi con i seguenti nomi: {all_cards}. Combina i significati di queste singole carte per prevedere il mio futuro.'
        # add languages here 

        # we generate the reply of the fortune teller (so the user can begin reading while waiting the image to be generated)
        replydict = generate_ai_text(text_prompt, self.seed)
        self.text_model = replydict["model"]
        first_summary = replydict["reply"]

        # enter conversation loop
        summary = first_summary
        while True:            
            print(f"{self.standard_phrases_dict["referrer"]}: {summary}")
            if self.language == "English":
                print("\nFortune teller: do you want to ask me anything about this interpretation?")
            elif self.language == "Italiano":
                print("\nCartomante: vuoi chiedermi qualcosa riguardo questa interpretazione?")
            loop_user_reply = input(f"\n{self.username}: ")
            if loop_user_reply in ["no", "no!", "No", "NO", "No!", "NO!"]:
                print(f"{self.standard_phrases_dict["referrer"]}: ok")
                time.sleep(2)
                if self.language == "English": print("\nFortune teller: bye!")
                elif self.language == "Italiano": print("\nCartomante: ciao!")
                return first_summary
            else:
                summary = generate_ai_reply(self.text_model, loop_user_reply)


    def forget_old_profecies(self) -> None:
        self.card_title_history = []
        self.prev_msgs = []
        self.current_card = ""



if __name__ == "__main__":
    # print(pollinations.Image.models())
    # print(pollinations.Text.models())
    for language_test in ["English", "Italiano"]:
        cartomante = Fortune_Teller(language_test)
        cartomante.pick_card()
        print(cartomante.hear_the_ancient_voices())
        image = cartomante.look_at_the_crystall_ball(True)
        cartomante.pick_card()
        print(cartomante.hear_the_ancient_voices())
        image = cartomante.look_at_the_crystall_ball(True)
        cartomante.pick_card()
        print(cartomante.hear_the_ancient_voices())
        image = cartomante.look_at_the_crystall_ball(True)
        print(cartomante.summarize_profecies())
        cartomante.forget_old_profecies()
