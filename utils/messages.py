from googletrans import Translator, LANGCODES

language_list = list(LANGCODES.keys())

class Messages_translator:
    __lang = ""
    __trans = Translator()

    def __init__(self, language: str, to_eng: bool | None = False):
        Messages_translator.__lang = LANGCODES[f"{language.lower()}"]
        if to_eng == True:
            self.from_lang = Messages_translator.__lang
            self.to_lang = "en"
        else:
            self.from_lang = "en"
            self.to_lang = Messages_translator.__lang

    def translate(self, *args):
        if Messages_translator.__lang == "en":
            return list(args)
        else:
            for_translated_list = list(args)
            translated_list = Messages_translator.__translate_list(self, for_translated_list)
            if len(translated_list) == 1:
                return translated_list[0]
            else:
                return translated_list

    def __translate_text(self, _text: str):
        if type(_text) != str:
            raise TypeError("Only str could be translated.")
        trs = Messages_translator.__trans
        return trs.translate(_text, src=self.from_lang, dest=self.to_lang).text

    def __translate_list(self, _list: list) -> list:
        instance_list = list()
        for item in _list:
            if type(item) == str:
                item_trs = Messages_translator.__translate_text(self, item)
            elif type(item) == list:
                item_trs = Messages_translator.__translate_list(self, item)
            elif type(item) == dict:
                item_trs = Messages_translator.__translate_dict(self, item)
            else:
                raise TypeError("How could...? You've got an error in list translation")
            instance_list.append(item_trs)
        return instance_list

    def __translate_dict(self, _dict: dict) -> dict:
        instance_dict = dict()
        dict_keys_list = list(_dict.keys())
        dict_values_list = list(_dict.values())
        for index, value in enumerate(dict_values_list):
            if type(value) == str:
                value_trs = Messages_translator.__translate_text(self, value)
            elif type(value) == dict:
                value_trs = Messages_translator.__translate_dict(self, value)
            elif type(value) == list:
                value_trs = Messages_translator.__translate_list(self, value)
            else:
                raise TypeError("How could...? You've got an error in dict translation")
            instance_dict[f"{dict_keys_list[index]}"] = value_trs
        return instance_dict

class UI_messages(Messages_translator):
    __system_messages_dict = {
        "choice":
        """Choose & please!""", # & == something
        "write":
        """Write & please!""", # & == i.e. your api key
        "wait":
        """Please wait a moment...""",
        "complete":
        """Action complete!""",
        "send_to_ai":
        """Send a message to the ai!""",
        "reset":
        """Reset""",
        "poop_info_request":
        """Tell me some informations about your baby's poop!""",
        "color_info" : {
            "request" :
            """Write your baby's poop color.""",
            "examples":
            """Red or Green or Black... or else""",
            "error":
            """You must tell me about poop color!"""
            },
        "form_info" : {
            "request":
            """Choose the baby poop's form""",
            "contents": ["severe diarrhea", "diarrhea", "normal", "constipation", "severe constipation"]
            },
        "blood_info" : {
            "request":
            """Does your baby's poop have any blood?""",
            "contents": ["not-bloody", "bloody",]
            },
        "RAG_error":
        """You have to prepare RAG thorough left sidebar for me to diagnosis.""",
        "model_error":
        """You have to set a chat model thorough left sidebar for me to diagnosis."""
    }
    __ai_messages_dict = {
        "intro" :
        """Hi! I'm baby poop expert... And I'm here for YOU! 
        \nBut wait... I need some information about your baby's poop.
        \nCan you fill the form below for me to help you?
        \nOh, I recommend you to do something on your left sidebar first!""",

        "form_submitted" :
        """The form submitted! You can fold the form above.")
        \nOkay. Now I know that your baby's poop was {poop_form}, {poop_color}, and {blood_form}
        \nIs there something more to tell me about your baby? Tell me about it in one message!""",

        "check_user_input" :
        """Do you think the explanation you sent is enough?
        \nPlease correct and send the explanation until you are satisfied, and press the button below if you are satisfied""",

        "chain" :
        """Okay. Just give me a few minutes, or just seconds. I'll help you.""",
        }
    __user_messages_dict = {
        "user_confirmed":
        """I am satisfied with my explanation.""",
    }

    @classmethod
    def system_messages(cls):
        return super().translate(cls.__system_messages_dict)
    @classmethod
    def ai_messages(cls):
        return super().translate(cls.__ai_messages_dict)
    @classmethod
    def user_messages(cls):
        return super().translate(cls.__user_messages_dict)