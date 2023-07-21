import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import   ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate, SystemMessagePromptTemplate
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import openai
openai.api_key = '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'

from utils import get_pdf_text, get_text_chunks, get_vectorstore

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

def simplify_text(text):
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt='simplify this text (ELI5): '+ f" '''{text}'''",
      max_tokens=100,
      temperature=0.2
    )
    return response.choices[0].text.strip()

def handle_userinput(user_question):

    response = st.session_state.conversation({'question': user_question})
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
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload class documents here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)



    #user_question = st.text_input("Ask a question about your class:")
    #if user_question:
    #    handle_userinput(user_question)


    def simplify_last_message():
        last_message = st.session_state.chat_history[-1].content
        simplified_text = simplify_text(last_message)        
        st.session_state.chat_history[-1].content = simplified_text
    st.button('Simplify', on_click=simplify_last_message)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Talk to Study Buddy"):
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


if __name__ == '__main__':
    main()