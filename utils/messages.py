class UI_messages:
    __system_messages_dict = {
        "title":
        """Chatbot for you!""",
        "choice":
        """Choose""",
        "write":
        """Write""",
        "wait":
        """Please wait a moment...""",
        "complete":
        """Action complete!""",
        "send_to_ai": {
            "request":
            """Send a message to the ai!""",
            "error":
            """Oh... you might forget to fill the form above! Can you double-check? I need some information about your baby's poop to help you!"""
        },
        "reset":
        """Reset""",
        "poop_info_request":
        """Tell me some informations about your baby's poop!""",
        "choose_number_of_data":
        """How many data do you have?""",
        "left_form_num":
        """more information needed.""",
        "time_data":
        """When did the baby start to defecate as below?""",
        "form": {
            "color_info" : {
                "request" :
                """What was the color of your baby's stool?""",
                "contents":
                ["red", "green", "black", "white", "brown", "ambiguous"],
                "suffix":
                """The color of my baby's stool was {contents}."""
                },
            "form_info" : {
                "request":
                """What was the baby's fecal form like?""",
                "contents":
                ["very hard", "hard", "a little hard", "formed", "loose", "very loose", "watery"],
                "suffix":
                """My baby's stool was in the form of {contents} material."""
                },
            "blood_info" : {
                "request":
                """Did your baby's feces have any blood?""",
                "contents":
                ["none of", "subtle", "red jelly shaped", "red mucus shaped", "melena", "linear shaped", "isolated snot shaped", "grain shaped"],
                "suffix":
                """The {contents} blood was seen at my baby's stool."""
                },
            "property_info" : {
                "request":
                """Was there something special on your baby's stool?""",
                "contents":
                ["nothing", "many amounts of protein lumps", "little amounts of protein lumps", "lots of mucus", "little mucus"],
                "suffix":
                """On the stool of my baby, there is {contents} remarkable."""
            }
            },
        "RAG":{
            "request":
            """Start preparation for < R A G >!""",
            "error":
            """You have to prepare RAG thorough left sidebar for me to diagnosis."""
            },
        "model": {
            "request":
            """Load <Chat_model>!""",
            "error":
            """You have to set a chat model thorough left sidebar for me to diagnosis."""
            },
        "chain": {
            "num":
            """How many documents do you wanna contain for <<RAG search>?""",
            "start":
            """Start making diagnosis"""
        },
        "chat": {
            "start":
            """You can start chat about the diagnosis now on!""",
            "label":
            """Chat Start!"""
        }
    }
    __ai_messages_dict = {
        "intro" :
        """Good day. I am present to alleviate your concerns. 
        \nIt brings me satisfaction to know that you have entrusted me with aiding in the resolution of your worries.
        \nI am committed to offering my utmost efforts to address your concerns.
        \nMight you kindly provide details regarding the infant's symptoms?""",

        "form_submitted" :
        """Understood. I believe I have an understanding of the symptoms the baby exhibited.
        \nAdditionally, do you have any further information you would like to provide?
        \nPlease feel free to share any additional details.""",

        "check_user_input" :
        """Do you think the explanation you sent is enough?
        \nPlease correct and send the explanation until you are satisfied, and press the button below if you are satisfied""",

        "chain" :
        """Understood. Could you please wait for a moment?
        \nI will provide an assessment of the baby's health status within a few minutes."""
        }
    __user_messages_dict = {
        "user_confirmed":
        """I am satisfied with my explanation."""
    }

    @classmethod
    def system_messages(cls):
        messages = cls.__system_messages_dict
        return messages
    @classmethod
    def ai_messages(cls):
        messages = cls.__ai_messages_dict
        return messages 
    @classmethod
    def user_messages(cls):
        messages = cls.__user_messages_dict
        return messages

    @classmethod
    def format_messages_for_form(cls):
        form_choices_dict = dict()
        form_suffix_dict = dict()
        form_option_list = list(cls.__system_messages_dict["form"].keys())
        for item in form_option_list:
            form_choices_dict[item] = cls.__system_messages_dict["form"][item]["contents"]
            form_suffix_dict[item] = cls.__system_messages_dict["form"][item]["suffix"]
        return form_choices_dict, form_suffix_dict