import pandas as pd
import numpy as np
import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from time import sleep
from hugchat_api import HuggingChat
import os
import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import requests
import tabulate
import classes

 

with st.sidebar:
    ti=st.title("Welcome to 😃AllTalK💬!")
    st.write('Developed By [Jordana](https://www.linkedin.com/in/manye-jordana-0315731b1)')
    st.markdown('For any enquiries contact me [here](https://myportfolio.com)!')
page=st.selectbox("WHAT I OFFER !",("Select","AI ChatBot","AI Summarizer","AI Visualizer"))


def main():
    def chatbot():
        st.title("😊 AllTalK 💬")
        st.markdown('''
        - Hey there i'm AllTalk 💬, your new AI friend 😊.
        - I may produce inacurate information about people, places, or facts
        - I have limited knowledge of the world and events after 2021 but i'm trained to help you the best i can and soon with more training i'll be a knowItAll !
        - Stick with me until then to be aware of everything before everyone 💡 ! 
         ''')
            
        EMAIL = st.secrets["DB_EMAIL"]
        PASSWD = st.secrets["DB_PASS"]
        COOKIE_STORE_PATH = "./usercookies"

        #HUG= HuggingChat(max_thread=1)

        #sign=HUG.getSign(EMAIL,PASSWD)
        #try:
        #    cookies=sign.login(save=True,cookie_dir_path=COOKIE_STORE_PATH)
        #except Exception as e:
        #    st.error(f"An error occurred during login: {str(e)}")
        #    st.stop()
        #cookies=sign.loadCookiesFromDir(cookie_dir_path=COOKIE_STORE_PATH)

        # Store LLM Generated responses
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]


        # Display  chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


        # Funtion genrating LLM response
        def generate_response(dialogue_history):
            #Hugging face login
            sign = Login(EMAIL, PASSWD)
            cookies = sign.login()
            # Create ChatBot
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            return chatbot.chat(dialogue_history)
        
        # User-provided prompt
        if prompt := st.chat_input("How may I help you ?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Append the dialogue history to the user's prompt
            dialogue_history = "\n".join([message["content"] for message in st.session_state.messages])
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)


        # Genrate a new response if last message not from the assistant(chatbot)
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    message_placeholder = st.empty()
                    full_response = ""

                try:
                    for response in generate_response(dialogue_history):
                        full_response += response
                        message_placeholder.markdown(full_response + " ")
                        sleep(0.01)
                    message_placeholder.markdown(full_response)

                    #checking if there are follow-up questions
                    if "?" in prompt:
                        #Update the chat history with the bot's response
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        #Clear the chat input box
                        st.session_state.prompt = ""
                        #set the chat input box value to the assistant's response
                        st.chat_input("Follow-up question", value=full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})

    def visualizer():
        st.header("😊 AllVisuals 📈")
        st.markdown('''
        - Hey there i'm AllVisuals 📈, your new AI Exploratory data analyst 😊.
        - I produce answers and stunning visuals from the data you give me.
        - Just Upload your dataset and ask your questions 💡 !
        ''')
        
        def load_csv(input_csv):
            df = pd.read_csv(input_csv)
            with st.expander('See DataFrame'):
                st.write(df)
            return df

        # Generate LLM response
        def generate_response(csv_file, input_query):
            llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0.2, openai_api_key=openai_api_key)
            df = load_csv(csv_file)
            # Create Pandas DataFrame Agent
            agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
            # Perform Query using the Agent
            response = agent.run(input_query)
            return st.success(response)

        # Input widgets
        uploaded_file = st.file_uploader('Upload a CSV file', type=['csv'])
        question_list = [
            'How many rows are there ?',
            'What is the datatype of each column ?',
            'Are they missing values ?',
            'Other']
        query_text = st.selectbox('Select an example query:', question_list, disabled=not uploaded_file)
        openai_api_key = st.text_input('OpenAI API Key', type='password', disabled=not (uploaded_file and query_text))

#____________________________________________________________________________#

        #dataset_container = st.empty()

        # App logic
        if query_text == 'Other':
            query_text = st.text_input('Enter your query:', placeholder = 'Enter query here ...', disabled=not uploaded_file)
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        if openai_api_key.startswith('sk-') and (uploaded_file is not None):
            st.header('Output')
            generate_response(uploaded_file, query_text)
        
        #llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0.2, openai_api_key=openai_api_key)
        available_models = {"ChatGPT-3.5": "gpt-3.5-turbo",}

        # Radio buttons for dataset choice
        chosen_dataset = uploaded_file

        # Check boxes for model choice
        st.write(":brain: Choose your model(s):")
        # Keep a dictionary of whether models are selected or not
        use_model = {}
        for model_desc,model_name in available_models.items():
            label = f"{model_desc} ({model_name})"
            key = f"key_{model_desc}"
            use_model[model_desc] = st.checkbox(label,value=True,key=key)

        # Text area for query
        question = st.text_area(":eyes: What would you like to visualise?", disabled=not (uploaded_file and query_text and openai_api_key), height=10)
        go_btn = st.button("Go...", disabled=not (uploaded_file and query_text and openai_api_key and question))

        # Execute chatbot query
        if go_btn > 0:
            # Place for plots depending on how many models
            plots = st.columns()
        
            # Format the question
            question_to_ask = format_question(primer1,primer2 , question)

        model_list = [model_name for model_name, choose_model in use_model.items() if choose_model]
        model_count = len(model_list)

        # Execute chatbot query
        if go_btn and model_count > 0:
            # Place for plots depending on how many models
            plots = st.columns(model_count)
            # Get the primer for this dataset
            primer1,primer2 = classes.get_primer(datasets[chosen_dataset],'datasets["'+ chosen_dataset + '"]')
            # Format the question
            question_to_ask = classes.format_question(primer1,primer2 , question)    
            # Create model, run the request and print the results

        # Create model, run the request and print the results
        for plot_num, model_type in enumerate(model_list):
            with plots[plot_num]:
                st.subheader(model_list)
                try:
                    # Run the question
                    answer=""
                    answer = classes.run_request(question_to_ask, available_models[model_type], key=my_key)
                    # the answer is the completed Python script so add to the beginning of the script to it.
                    answer = primer2 + answer
                    plot_area = st.empty()
                    plot_area.pyplot(exec(answer))           
                except Exception as e:
                    if type(e) == openai.error.APIError:
                        st.error("OpenAI API Error. Please try again a short time later.")
                    elif type(e) == openai.error.Timeout:
                        st.error("OpenAI API Error. Your request timed out. Please try again a short time later.")
                    elif type(e) == openai.error.RateLimitError:
                        st.error("OpenAI API Error. You have exceeded your assigned rate limit.")
                    elif type(e) == openai.error.APIConnectionError:
                        st.error("OpenAI API Error. Error connecting to services. Please check your network/proxy/firewall settings.")
                    elif type(e) == openai.error.InvalidRequestError:
                        st.error("OpenAI API Error. Your request was malformed or missing required parameters.")
                    elif type(e) == openai.error.AuthenticationError:
                        st.error("Please enter a valid OpenAI API Key.")
                    elif type(e) == openai.error.ServiceUnavailableError:
                        st.error("OpenAI Service is currently unavailable. Please try again a short time later.")                   
                    else:
                        st.error("Unfortunately the code generated from the model contained errors and was unable to execute. ")
        
        # Display the datasets in a list of tabs
        # Create the tabs
        tab_list = st.tabs(datasets.keys())

        # Load up each tab with a dataset
        for dataset_num, tab in enumerate(tab_list):
            with tab:
                # Can't get the name of the tab! Can't index key list. So convert to list and index
                dataset_name = list(datasets.keys())[dataset_num]
                st.subheader(dataset_name)
                st.dataframe(datasets[dataset_name],hide_index=True)


    def summarizer():

        # Hide menu and footer
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        
        # Insert footer to reference dataset origin  
        footer="""<style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;text-align: center;}</style><div class="footer">
        <p> <a style='display: block; text-align: center;'> Datasets courtesy of NL4DV, nvBench and ADVISor </a></p></div>"""
        st.caption("Datasets courtesy of NL4DV, nvBench and ADVISor")




    if page == "Select":
        st.write("Please select the services")
    elif page == "AI ChatBot":
        chatbot()
    elif page == "AI Visualizer":
        visualizer()  
    else:
        summarizer()
  
if __name__=='__main__':
    main()
