import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import   ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate, SystemMessagePromptTemplate
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import openai
import os

from utils import get_pdf_text, get_text_chunks, get_vectorstore,load_vectorstore

openai.api_key = os.getenv('OPENAI_API_KEY')
MAX_CHATGPT35_TOKENS=4095

def get_conversation_chain(vectorstore, student='the student'):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    general_system_template =  f""" 
    You are speaking to {student}, and guiding them through through their inquiries. 
    If the student's major is provided, greet them by their name and cater your responses to their major.
    For example, provide a metaphor that relates the response to the student's major' 
    ----
    {{context}}
    ----
    """
    general_user_template = f"Hi I am {student}. Here is my inquiry: ```{{question}}```"

    #print(general_system_template)
    #print(general_user_template)

    messages = [
                SystemMessagePromptTemplate.from_template(general_system_template),
                HumanMessagePromptTemplate.from_template(general_user_template)
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)


    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={'prompt': qa_prompt},
        max_tokens_limit=MAX_CHATGPT35_TOKENS
    )
    return conversation_chain


def simplify_text(text):
    print(text)
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      
      #messages='Simplify the following text: '+ f" '''{text}'''",
      messages=[
        {"role": "system", "content": "You are Simplify. You rewrite complex texts with 2 rules 1) you simplify the text so that a 12 year old would understand and 2) you refrain from using complex terms."},
        {"role": "user", "content": text},
        ],
      max_tokens=3000,
      temperature=0.2,
      
    )
    print(response)
    return response.choices[-1].message.content
    



def handle_userinput(prompt):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = "loading..."
        message_placeholder.markdown(full_response)

    
    
    response = st.session_state.conversation({'question': prompt})
    st.session_state.chat_history = response['chat_history']

    full_response = st.session_state.chat_history[-1].content
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})



def main():


    load_dotenv()
    st.set_page_config(page_title="Study Buddy",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    with st.sidebar:

        st.header("Your classes:")

        #classes are currently determined by what is in the "vectors" folder
        classes = [name for name in os.listdir("vectors")]
        if '.DS_Store' in classes: #mac bug, probably can be removed for huggingface
            classes.remove('.DS_Store')
        classes.sort()
        st.session_state.classes=classes
        if 'radioIndex' not in st.session_state:
            st.session_state.radioIndex = 0

        className = st.radio(
            "Choose your class",
            st.session_state.classes,
            index=st.session_state.radioIndex
            )

        
        #load vectors for the class selected
        vectorstore = load_vectorstore(className)
        st.session_state.conversation = get_conversation_chain(vectorstore)

        if 'addNewClass' not in st.session_state:
            st.session_state.addNewClass = False

        def addNewClass(i):
            st.session_state.addNewClass = i

        st.button('Add new class', on_click=addNewClass, args=[True])

        if st.session_state.addNewClass:
            newClassName = st.text_input("Enter the name of your class:")
            pdf_docs = st.file_uploader(
                "Upload class documents here and click on 'Process'", accept_multiple_files=True)
            if st.button("Process"):
                with st.spinner("Processing"):
                    # get pdf text
                    raw_text = get_pdf_text(pdf_docs)

                    # get the text chunks
                    text_chunks = get_text_chunks(raw_text)

                    # create vector store
                    vectorstore = get_vectorstore(text_chunks, str(len(st.session_state.classes)+1) + "_" + newClassName)

                    # create conversation chain
                    st.session_state.conversation = get_conversation_chain(
                        vectorstore)

                #update UI    
                st.session_state.classes.append(newClassName)
                st.session_state.radioIndex = len(st.session_state.classes)-1
                addNewClass(False)
                st.experimental_rerun()

                  

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.caption("StudyBuddy transforms your existing course content into your preferred learning styles!")

    # if not processed first, this will break. 
    def change_student():
        option = st.session_state['student']
        student_data = 'the student'
        if(option == 'Choose Student'):
            return
        elif(option == 'Billy'):
            student_data = "Billy, the Biology major. "
        elif(option == 'Christina'):
            student_data = "Christina, the Chemistry major. "

        st.session_state.conversation = get_conversation_chain(vectorstore, student_data)
        st.session_state.messages = []

    # Choose Student Profile 
    option = st.selectbox(
    '',
    ('Choose Student', 'Billy', 'Christina'),
    on_change=change_student,
    key='student')
    

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Talk to Study Buddy"):
        handle_userinput(prompt)
        



    def simplify_last_message():
        last_message = st.session_state.chat_history[-1].content
        simplified_text = simplify_text(last_message)        
        st.session_state.chat_history[-1].content = simplified_text
        st.session_state.messages.append({"role": "assistant", "content": simplified_text})

    st.button('Simplify', on_click=simplify_last_message)


if __name__ == '__main__':
    main()