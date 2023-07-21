import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import   ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate, SystemMessagePromptTemplate
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import os

from utils import get_pdf_text, get_text_chunks, get_vectorstore,load_vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    general_system_template = r""" 
    Given a specific context, please guide the student through their inquiries. 
    If the topic information is not provided in the prompt, say, 'You're off topic. FOCUS.' 
    ----
    {context}
    ----
    """
    general_user_template = "```{question}```"
    messages = [
                SystemMessagePromptTemplate.from_template(general_system_template),
                HumanMessagePromptTemplate.from_template(general_user_template)
    ]
    qa_prompt = ChatPromptTemplate.from_messages( messages )

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={'prompt': qa_prompt}
    )
    return conversation_chain


def handle_userinput(user_question, question_augmentation):
    response = st.session_state.conversation({'question': question_augmentation + user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


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

                    

    

    st.header("Study Buddy")
    st.write('You selected ' + className)
    difficulty = st.slider("Difficulty", min_value=1, max_value=5, value=5)
    question_augmentation=''
    if difficulty == 4:
        question_augmentation = f'Simplify your response so a high schooler would understand it: '
    elif difficulty == 3:
        question_augmentation = f'Simplify your response so a middle schooler would understand it: '
    elif difficulty == 2:
        question_augmentation = f'Simplify your response so an elementary schooler would understand it: '

    elif difficulty == 1:
        question_augmentation = f'Simplify your response so a 5 year old would understand it: '

    pwd_protected = st.text_input("Type in the password to use the app:")


    user_question = st.text_input("Ask a question about your class:")
    if user_question and pwd_protected == "Dream123":#st.secrets["SECRET_PASSWORD"]:
        handle_userinput(user_question, question_augmentation)



if __name__ == '__main__':
    main()