import os
import sys

from matplotlib.backends.backend_pdf import PdfPages

from fortune_teller.ai_utils import *
from fortune_teller.pdf_utils import _image_text_to_pdf, _text_to_pdf
"""
Enable the test mode to skip the actual fortune telling and just print the picked cards
TEST_MODE = True
"""

TEST_MODE = False


def main():
    # set the base path to the folder where the script is located
    basepath = os.path.split(os.path.dirname(__file__))[0]

    # set the path to the images folder and the pdf folder
    save_path = os.path.join(basepath, "generated_images")
    os.makedirs(save_path, exist_ok=True)

    pdf_save_path = os.path.join(basepath, "generated_predictions")
    os.makedirs(pdf_save_path, exist_ok=True)

    # select language
    language = ""
    while language == "":
        print("Select language [i = Italiano, e = English] then type enter")
        user_reply = input("\nUser: ")
        if user_reply == "e":
            language = "English"
        elif user_reply == "i":
            language = "Italiano"
        else:
            print("Not recognized\n\nSelect language: [i = italiano, e = english]")

    language_path = os.path.join(os.path.dirname(__file__), "Languages", language)
    cartomante = Fortune_Teller(language_path, save_path)

    # ask if the user wants to start
    print(
        f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['greeting']}"
    )
    done = False
    while not done:

        user_reply = input(f'\nUser: ')
        
        # if the user wants to start we enter the loop
        if user_reply in cartomante.standard_phrases_dict['yes']:

            # first we ask name, age, lucky number and favourite color     
            name = ""
            age = 20
            selected_number = ""
            selected_color = "green"
            infodone = False
            while not infodone:

                # first select the name
                print(
                    f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['question1']}"
                )
                name = input('\nUser: ')

                # then the age
                print(
                    f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['question2']}"
                )
                age = input(f'\n{name}: ')

                # favourite color
                print(
                    f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['question3']}"
                )                
                number_entry = input(f'\n{name}: ')
                try: selected_number = int(number_entry)
                except:  selected_number = number_entry

                # and lucky number
                print(
                    f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['question4']}"
                )
                selected_color = input(f'\n{name}: ')

                # ask if everything is correct, otherwise start again
                if language == 'English':
                    print(f'Fortune teller: so your name is {name}, your age is {age}, your lucky number is {selected_number} and your favourite color is {selected_color}, is that correct?')
                elif language == 'Italiano':
                    print(f'Cartomante: Quindi il tuo nome è {name}, la tua età è {age}, il tuo numero fortunato è {selected_number} e il tuo colore preferito è {selected_color}, giusto?')
                user_reply = input(f'\n{name}: ')
                if user_reply in cartomante.standard_phrases_dict['yes']:
                    print(
                    f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['confirm']}"
                    )
                    infodone = True
                # type "exit" to stop the program
                elif user_reply in "exit": sys.exit()


            person_dict = {'name' : name, 'age' : age, 'number' : selected_number, 'color' : selected_color}
            
            done = True

            # the loop runs until the user says no (or enters evil mode and says "shut up")
            contune_reading = True
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            with PdfPages(os.path.join(pdf_save_path, f'{timestamp}results.pdf')) as pdf:

                while contune_reading:

                    # first we pick a card
                    cartomante.pick_card()

                    # if test mode is enabled we just print the card and skip the rest
                    if TEST_MODE:
                        print(f"{cartomante.current_card}")

                    else:

                        # we get the profecy related to this card
                        current_profecy = cartomante.hear_the_ancient_voices(person_dict)
                        print(f"\n{cartomante.standard_phrases_dict['referrer']}: {current_profecy}")

                        # we change the image until the user is satisfied (i.e. says "yes")
                        right_image = False
                        newcard_prompt = ""
                        while not right_image:
                            image = cartomante.look_at_the_crystall_ball(True, newcard_prompt)
                            print(f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['like_image_string']}")
                            user_reply = input(f'\n{name}: ')
        
                            if user_reply in cartomante.standard_phrases_dict['yes']:
                                right_image = True
                            else:
                                print(f"\n{cartomante.standard_phrases_dict['referrer']}: ok")
                        
                                if user_reply in cartomante.standard_phrases_dict['no']:
                                    # if the user doesn't like the image we ask for a new one, keeping the same prompt but with a random seed (so it's always different)
                                    newcard_prompt = ""
                                else:
                                    # otherwise we give the user reply as prompt for the new image generation
                                    newcard_prompt = user_reply
                        
                        # save the current image to pdf and print the text on the side
                        _image_text_to_pdf(image, cartomante.current_card, current_profecy, pdf)

                    # ask the user if wants to continue reading
                    print(f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['continue_reading_future']}")
                    second_user_reply = input(f'\n{name}: ')

                    # if the user says yes or no it's ok, otherwise it gets angry (if not in test mode)
                    if second_user_reply in cartomante.standard_phrases_dict['yes']:
                        pass
                    elif second_user_reply in cartomante.standard_phrases_dict['no']:
                        contune_reading = False
                        if not TEST_MODE:
                            summary_of_profecies = cartomante.summarize_profecies()
                            _text_to_pdf(summary_of_profecies, pdf)
                    elif not TEST_MODE:
                        # now the fortune teller is MAD, the only way to stop is to yell SHUT UP! (zitto in italiano)
                        cartomante.punish_insolence(user_prompt = second_user_reply)
                        contune_reading = False
        
        
        # if the user don't want to start the fotune teller says goodbye 
        elif user_reply in cartomante.standard_phrases_dict['no']:
            done = True
            print(f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['goodbye']}")

        # if the user answered not no nor yes, the fortune teller gets confused
        else: print(f"\n{cartomante.standard_phrases_dict['referrer']}: {cartomante.standard_phrases_dict['confused']}")


if __name__ == "__main__":
    main()