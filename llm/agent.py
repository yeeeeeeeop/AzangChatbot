import os
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.utils import ConfigurableFieldSpec
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_community.chat_message_histories.streamlit import StreamlitChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent

def Chatting_agent(llm, main_path:str, chat_tools:list, agent_prompt):
    def User_Conversation_History(user_id: str, conversation_id: str):
        #return FileChatMessageHistory(file_path=os.path.join(main_path, "user", user_id+"--"+conversation_id+".json"))
        user_id+conversation_id
        return StreamlitChatMessageHistory(key= "chat_memory")
    
    chat_agent = create_tool_calling_agent(
        llm= llm,
        tools= chat_tools,
        prompt= agent_prompt
    )
    chat_executor = AgentExecutor(
        agent= chat_agent,
        early_stopping_method= "force",
        handle_parsing_errors= True,
        max_iterations= 10,
        tools= chat_tools,
        verbose= True
    )
    chatbot = RunnableWithMessageHistory(
        runnable= chat_executor,
        get_session_history= User_Conversation_History,
        input_messages_key= "input",
        output_messages_key= "output",
        history_messages_key= "chat_history",
        history_factory_config=[
            ConfigurableFieldSpec(
                id= "user_id",
                annotation= str,
                name = "User ID",
                description= "Unique identifier for the user.",
                default= "",
                is_shared= True
            ),
            ConfigurableFieldSpec(
                id= "conversation_id",
                annotation= str,
                name = "Conversation ID",
                description= "Unique identifier for the conversation.",
                default= "",
                is_shared= True
            )
        ]
    )
    return chatbot