import streamlit as st
from markdown_it import MarkdownIt
# from markdown_it_py import MarkdownIt #internally streamlit uses this as well, potential dependency conflict, be aware.
md = MarkdownIt()

from dotenv import load_dotenv
import pprint
import json
import os
import random
import re
import random
import uuid

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.messages.ai import AIMessageChunk
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
import time
import streamlit.components.v1 as components

from open_pdf_button import my_component

print(f"Loading environment, libraries, and resources...")

load_start_time = time.time()

load_dotenv()

import model_integrations
from model_config import Embedding_Model, Language_Model, Reranker_Model

# known bug with specific encoding of :
# 'Joint ESA Gls MiCAR %28JC 2024 28%29_EN'

st.set_page_config(layout='wide')

st.markdown("""
    <style>
        /* This targets the block containing the columns */
        .st-key-pdf-display-container {
            position: sticky;
            top: 70px; /* Adjust this value to align with your app's header */
            z-index: 1; /* Ensures the sticky element stays on top */
            display: flex;
            justify-content: center;
            # padding: 2rem 0;
        }
    </style>
    <style>
        .stMainBlockContainer {
            padding-bottom: 2rem;
            padding-right: 0.5rem;
            padding-left: 0.5rem;
        }
    </style>
    <style>
            .st-key-chat-input-container-key {
                position: sticky;
                left: 0px;
                bottom: 0px;
                width: 100%;
                z-index: 99;
            }
    </style>
    <style>
            .st-key-close-button {
                display: flex;
                justify-content: end;
                & > div {
                width: auto;
                }
            }
    </style>
    <style>
            [popover]{
                padding: .5rem 1rem;
                border-radius: 0.5rem;
                transition-duration: 0.1s;
                <!-- Copied from streamlit popover -->
                border-bottom-color: rgba(49, 51, 63, 0.2);
                border-top-color: rgba(49, 51, 63, 0.2);
                border-right-color: rgba(49, 51, 63, 0.2);
                border-left-color: rgba(49, 51, 63, 0.2);
                padding-top: calc(-1px + 1.5rem);
                padding-bottom: calc(-1px + 1.5rem);
                padding-left: calc(-1px + 1.5rem);
                padding-right: calc(-1px + 1.5rem);
                min-width: 20rem;
                max-width: calc(736px - 2rem);
                overflow: auto;
                max-height: 70vh;
                margin-bottom: 1rem;
                margin-right: 1rem;
                margin-top: 8px;
                transition-property: opacity, transform;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
                border-bottom-left-radius: 0.75rem;
                border-bottom-right-radius: 0.75rem;
                border-top-right-radius: 0.75rem;
                border-top-left-radius: 0.75rem;
                opacity: 1;
                background-color: rgb(255, 255, 255);
                transition-timing-function: cubic-bezier(0.2, 0.8, 0.4, 1);
                border-bottom-style: solid;
                border-top-style: solid;
                border-right-style: solid;
                border-left-style: solid;
                border-bottom-width: 1px;
                border-top-width: 1px;
                border-right-width: 1px;
                border-left-width: 1px;
            }
    </style>
    <style>
            button[popovertarget] {
                color: #0000EE;
                background-color: transparent;
                border: none;
                text-decoration: underline dotted;
            }
    </style>
""", unsafe_allow_html=True)


supports_thought = ["GEMINI_25_PRO"]

sidebar = st.sidebar

sidebar.header("User Config")
# order changed back, bug in upgraded version of Embedding_Model.GEMINI_EMBEDDING_001
embedding_model_option = sidebar.selectbox(
    "Which embedding model to choose",
    (Embedding_Model.GEMINI_EMBEDDING_001_SOLVENCY_II, Embedding_Model.QWEN_3_EMBEDDING_SOLVENCY_II),
    format_func=lambda x: x.value["display_name"]
)

reranker_model_option = None
if os.environ["ENABLE_RERANKER"] == "TRUE":
    reranker_model_option = sidebar.selectbox(
        "Which reranker model to choose",
        (Reranker_Model.QWEN_3_RERANKER, Reranker_Model.COHERE_35_RERANKER),
        format_func=lambda x: x.value["model"]
    )

llm_option = sidebar.selectbox(
"Which LLM to choose",
(Language_Model.AZURE_GPT_4O_MINI, Language_Model.GEMINI_25_PRO, Language_Model.AZURE_OPENAI_O4_MINI, Language_Model.GROK_4),
format_func=lambda x: x.value["model"]
)
k = sidebar.slider("Pieces of text retrieved (k)", 0, 20, 10)
top_n = sidebar.slider("Filtered after retrieved (max k)", 0, k, 3 if k >= 3 else k)

sidebar.header("Debugger")
debug_mode = sidebar.toggle(
    "Debug Mode",
    False
)

@st.cache_resource
def cached_embedding_model(embedding_model_option: Embedding_Model):
    return model_integrations.set_up_embedding_model(embedding_model_option)

@st.cache_resource
def cached_reranker_model(reranker_model_option: Reranker_Model, top_n: int = 3):
    if reranker_model_option is None:
        return None
    
    # unfortunately, the top_n is not configurable through ContextualCompressionRetriever
    return model_integrations.set_up_reranker_model(reranker_model_option, top_n=top_n)

@st.cache_resource
def cached_llm(llm_option: Language_Model):
    return model_integrations.set_up_llm(llm_option)

@st.cache_resource
def cached_vectorstore(embedding_model_option):
    return model_integrations.load_vectorstore(embedding_model_option)

# load models and vectorstore
# cached because streamlit reloads after each user input
embedding_model = cached_embedding_model(embedding_model_option)
reranker_model = cached_reranker_model(reranker_model_option, top_n)
llm = cached_llm(llm_option)
vectorstore = cached_vectorstore(embedding_model_option)

load_elapsed_time = time.time() - load_start_time
print(f"Elapsed time for loading libraries and vector database: {load_elapsed_time}s")

print(f"""---CONFIG---
llm {type(llm)}
embedding {type(embedding_model)}
debug {debug_mode}
---END OF CONFIG---
      """)


def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

generation_instructions = load_prompt("prompt/solvency_II_instructions.md")
system_instructions_dict = {"role": "system", "content": generation_instructions}

# INITIALIZE SESSION STATE
if "document_link_through_link" not in st.session_state:
    st.session_state["document_link_through_link"] = None

if 'pdf_to_display' not in st.session_state:
    st.session_state.pdf_to_display = None

if "messages" not in st.session_state:
    st.session_state["messages"] = [
    system_instructions_dict,
]
    
if "message_to_component" not in st.session_state:
    st.session_state.message_to_component = None
    
# if 'expanded_thoughts' not in st.session_state:
#     st.session_state.expanded_thoughts = False

# DISPLAY PDFS
def close_pdf_display():
    # update both session state
    # st.session_state["document_link_through_link"] = None
    # there should be an easier way to do this, but this works
    st.session_state.pdf_to_display = None
    print("PDF display closed.")
    st.session_state.message_to_component = {"type": "CLEAR_PDF"}


def set_pdf_to_display(pdf_link):
    # lambda: setattr(st.session_state, 'pdf_to_display', document_link)
    print(f"Setting pdf to display: {pdf_link}")
    st.session_state.pdf_to_display = pdf_link
    print(f"Set pdf to display: {st.session_state.pdf_to_display}")

def displayPDF(file_name):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join("app", "static")
    ALLOWED_PDF_DIR = os.path.join(APP_ROOT, STATIC_DIR)

    real_file_path = os.path.join(ALLOWED_PDF_DIR, file_name)

    print(f"Real file path: {real_file_path}")

    if not os.path.realpath(real_file_path).startswith(os.path.realpath(ALLOWED_PDF_DIR)):
        
        raise Exception("Path not allowed, only serves PDF from static folder ", ALLOWED_PDF_DIR)
    
    secure_file_path = os.path.join(STATIC_DIR, file_name)

    print("FILE_NAME: ", file_name)
    if file_name == "solvency-II-files\\guidelines-level 3-v0.1 - TRUNCATED\\Joint ESA Gls MiCAR %28JC 2024 28%29_EN.pdf":
        # naming issue, so renamed in static folder as well. temporary work around.
        print(f"File replaced: {real_file_path}")
        secure_file_path = os.path.join(STATIC_DIR, "solvency-II-files\\guidelines-level 3-v0.1 - TRUNCATED\\Joint ESA Gls MiCAR JC 2024_EN.pdf")

    # print("Displaying pdf with: ", secure_file_path)
    pdf_display = f'<iframe id=pdf_sidebar src="{secure_file_path}" width="700" height="550" type="application/pdf"></iframe>'
    
    # Displaying File
    with st.container(key="pdf-display-container"):
        st.button(key="close-button", label="close", on_click=close_pdf_display, icon="❌")
        st.markdown(pdf_display, unsafe_allow_html=True)

if st.session_state.message_to_component:
    message = st.session_state.message_to_component
    components.html(f"""
        <script>
            const componentFrame = window.parent.document.querySelector('.st-key-messenger iframe');
            if (componentFrame) {{
                console.log('Sending message to component:', {json.dumps(message)});
                componentFrame.contentWindow.postMessage({json.dumps(message)}, '*');
            }} else {{
                console.error('Could not find the component iframe to send message.');
            }}
        </script>
    """, height=0, width=0)
    # Important: Clear the message after sending it to prevent resending on subsequent reruns
    st.session_state.message_to_component = None

# SETTING STATE FOR DISPLAY PDF THROUGH FOR BUTTONS IN POPOVER
with sidebar:
    document_link_through_link = my_component("Debugger for messenger", "messenger")
    prev_document_link_through_link = st.session_state.get("document_link_through_link", None)

print(f"Document link through link: {document_link_through_link}, prev: {prev_document_link_through_link}   ")
if document_link_through_link != prev_document_link_through_link:
    print(f"Changed Document Link: {document_link_through_link}, previous: {prev_document_link_through_link}")
    print(f"type of document link: {type(document_link_through_link)}, previous: {type(prev_document_link_through_link)}")
    # update pdf to display if change is detected
    # st.session_state.pdf_to_display = document_link_through_link
    if document_link_through_link == 0 and prev_document_link_through_link != 0:
        print("PDF is cleared")
        # st.session_state.document_link_through_link = None
    else: 
        set_pdf_to_display(document_link_through_link) 
    st.session_state["document_link_through_link"] = document_link_through_link

print(f"Loaded document link link: {document_link_through_link}")

# DISPLAY SOURCES FUNCTION
def displaySources(document_sources):
    added_sources = []
    deduplicated_document_sources = []
    for document_source in document_sources:
        if document_source["link"] not in added_sources:
            # check if title is not set in metadata
            # print(f"Title: used {title}")
            
            added_sources.append(document_source["link"])
            deduplicated_document_sources.append(document_source)
    
    container_key = f"sources-buttons-container-{deduplicated_document_sources[0]["query_id"]}".replace(" ", "-")

    # TO CHANGE. Include in global styling with container_key start with sources-container-
    st.markdown(
        f"""
        <style>
            .st-key-{container_key} {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 2fr));
                gap: 1rem;
            }}
        </style>
        """, unsafe_allow_html=True
    )
    
    with st.container(border=True):
        with st.container(key=container_key):
            for document_source in deduplicated_document_sources:
                document_link = document_source["link"]

                TITLE_LENGTH_LIMIT = 50

                truncated_title = document_source["title"] if len(document_source["title"]) <= TITLE_LENGTH_LIMIT else document_source["title"][:TITLE_LENGTH_LIMIT] + "..."

                print(f"Document link: {document_source["link"]}")
                st.button(
                    key=f"{document_source["query_id"]}---{document_source["link"]}",
                    label=f"{truncated_title}", 
                    on_click= set_pdf_to_display, 
                    args=(document_link, ), #args in python need to give not wrapped with function as in js
                    icon="🔗"
                )


 # LAYOUT OF MAIN PAGE
chat_col, pdf_col = st.columns([1, 1])

with chat_col:
    chat_col.title("💬 Regulation Search")
    chat_col.caption("🚀 Powererd by Triple A")

    with st.popover("test"):
        st.markdown("# Test")
    
# PDF INTERFACE
if st.session_state.pdf_to_display:
    # WARNING : pdf_to_display through buttons in displaySources OR by clicking on buttons in the popovers.
    print("pdf: ", st.session_state.pdf_to_display)
    with pdf_col:
        displayPDF(st.session_state.pdf_to_display)    

popover_elements_event_listener = """
<script>
    window.onload = (event) => {
        console.log("Window loaded, adding event listeners to popover buttons");
        const componentFrame = window.parent.document.querySelector('.st-key-messenger').querySelector('iframe');
        if (!componentFrame) {
            console.error("Component iframe not found!");
            return;
        }

        const componentWindow = componentFrame.contentWindow;
                
        // Add event listeners to all buttons with the class 'popover'
        const popover_elements = window.parent.document.querySelectorAll('[id^=\"pop-button\"]');
        function handlePopoverClick(event) {
            const button = event.currentTarget;
            const documentLink = button.dataset.documentLink;
            console.log(documentLink)
            // button.style.color = "red";
            componentWindow.postMessage({
                type: 'POPOVER_CLICKED',
                documentLink: documentLink
            }, '*'); // In production, use the component's actual origin instead of '*'

        }
        popover_elements.forEach(element => {element.addEventListener("click", (e) => {handlePopoverClick(e)})})
    }
</script>
"""

# CHAT INTERFACE
with chat_col:
    messages_container = chat_col.container()
    messages_container.chat_message("assistant").write("Hello I am here to help search through documents related to Solvency II")
    for message in st.session_state.messages:
        # do not print out system prompt
        if message["role"] == "system":
                continue
        
        if "thoughts" in message and message["thoughts"] != "":
            with messages_container.chat_message("assistant", avatar="💭"):
                thought_expander = st.expander("**Thoughts...**")
                thought_expander.write(message["thoughts"])

        # message version 1, with raw html
        with messages_container.chat_message(message["role"]):
            if "popover_elements" in message and message["popover_elements"] != "":
                # load in event listeners for popover buttons
                components.html(popover_elements_event_listener, height=0, width=0) 
                st.html(message["popover_elements"])
            st.markdown(message["content"], unsafe_allow_html=True)

        if "sources" in message:
            with messages_container.chat_message("assistant", avatar="🔗"): 
                print("message sources: ")
                pprint.pprint(message["sources"])
                displaySources(message["sources"])

    if query := st.chat_input(key="chat-input-container-key"):
        model_name = llm.__dict__.get("model_name") or llm.__dict__.get("model").split("models/")[1] #model name stored somewhere different depending on Azure or Google integration of Langchain
        if debug_mode:
            messages_container.chat_message('assistant').info(model_name)
        print(f"Running query with model: {model_name}")
        if llm_option.value["model"] != model_name:
            raise Exception(f"Option not respected, running {model_name}, while expecting {llm_option.value["model"]}")
        if debug_mode:
            messages_container.info(f"Running query with model: {model_name}")
        messages_container.chat_message("user").write(query)

        # print(f"First documents of all matched documents: {matched_documents[0].__dict__}")
        
        chunks_concatenated = ""
        document_sources = []
        query_id = str(uuid.uuid4())
        if embedding_model_option.value["data-ingestion-pipeline"] == "v1":
            raise Exception("No longer supported, use v2 data ingestion pipeline (reason reranker).")
        
            for idx, document in enumerate(matched_documents):
                source = f"{document.metadata["source"]} on page {document.metadata["page_label"]}"
                #note: unsure why metadata has a page and page_label attribute?, verified that page_label was correct for data kwality pdf
                document_sources.append(source)
                chunks_concatenated += f"###\n source {idx}, ref {source}:\n\n {document.page_content} \n\n\n"
        elif embedding_model_option.value["data-ingestion-pipeline"] == "v2":
            matched_documents = None
            if reranker_model is None:
                matched_documents = vectorstore.similarity_search(query=query,k=k)
                # matched_documents = reranker_model.rerank(query=query, documents=matched_documents)
            else:
                print(f"Reranking documents with {reranker_model_option.value['model']}")
                retriever = vectorstore.as_retriever(search_kwargs={"k": k})
                compressor = ContextualCompressionRetriever(base_compressor=reranker_model, 
                                            base_retriever=retriever
                )

                reranked_documents = compressor.invoke(query)

                matched_documents = reranked_documents

            for idx, chunk in enumerate(matched_documents):

                source_index = idx + 1

                print("PRINTING CHUNK METADATA:")
                pprint.pprint(chunk.metadata)
                print("END OF PRINT CHUNK METADATA")

                # define metadata
                title = ""
                if "title" in chunk.metadata and chunk.metadata["title"] != "":
                    title = chunk.metadata["title"]
                else: 
                    title = str(chunk.metadata["source"]).split("data\\raw\\solvency-II-files\\")[-1]
                    title = title.replace("guidelines-level 3-v0.1 - TRUNCATED\\", "guidelines-level-3: ")


                source_metadata = ""
                source_metadata += f"* Title: {title}"
                source_metadata += f"\n* keywords: {chunk.metadata["keywords"]}\n" if "keywords" in chunk.metadata  and chunk.metadata["keywords"] != "" else ""
                source_metadata += f"\n* Author: {chunk.metadata["Author"]}\n" if "Author" in chunk.metadata else ""
                source_metadata += f"\n* Header 1: {chunk.metadata["Header 1"]}\n" if "Header 1" in chunk.metadata else ""
                source_metadata += f"\n* Header 2: {chunk.metadata["Header 2"]}\n" if "Header 2" in chunk.metadata else ""
                source_metadata += f"\n* Header 3: {chunk.metadata["Header 3"]}\n" if "Header 3" in chunk.metadata else ""

                # deduplicated list of document sources, used at end of chat
                print(f"chunk metadata: source {chunk.metadata["source"]}")

                # example: chunk.metadata["source"] == data\raw\solvency-II-files\solvency II - level 2.pdf
                print(f"split: {str(chunk.metadata["source"]).split("data\\raw\\")}")



                # document_source is the UI data format, used to both display pdf sources, and page_content on click
                document_source = {
                        "source_index": source_index,
                        "link": str(chunk.metadata["source"]).split("data\\raw\\")[-1],
                        "title": title,
                        "page_content": chunk.page_content,
                        "query": query,
                        "query_id": query_id
                    }

                document_sources.append(document_source)

                chunks_concatenated += f"\n ### source {source_index} \n\n metadata:\n {source_metadata}:\n\n extract:\n\n {chunk.page_content} \n\n\n"
        else:
            raise Exception("Way of displaying metadata from data ingestion pipeline not implemented")


        print(f"CHUNKS CONCATENATED FOR {source_index}: {chunks_concatenated}")
        print(f"DOCUMENT SOURCE: {document_sources}")

        # NOT IN USE YET, CAN BE USEFUL FOR VERIFICATION
        #source: https://docs.llamaindex.ai/en/stable/examples/workflow/citation_query_engine/
        # citation_instructions = """
        # Please answer the following question using only the information provided in the numbered sources below. When you reference information from a source, cite the corresponding source number(s) in brackets (e.g., [1]). Every answer must include at least one citation, but you should only cite a source if you are explicitly referencing it. If none of the sources are relevant or helpful, clearly state that in your response.

        prompt = f"""
        ## Question
        \n\n {query} \n\n
        \n## Context
        \n\n {chunks_concatenated} \n\n
        \n## Answer
        \n\n When answering reference ONLY if applicable source with (Source <insert number>). Answer based on the mentioned sources in the Context answer the Question. 
        \n\n
        """

        # add sources to session state
        print(f"Document sources: {document_sources}")

        st.session_state.messages.append({"role": "user", "content": query})
        
        # change to add the context of previous parts.
        template = ChatPromptTemplate([("system", generation_instructions) , ("user", prompt)])

        formatted_message = template.format_messages()
        
        print(f"PROMPT FOR LLM: \n\n")
        pprint.pprint(formatted_message)      
        print("\n\n END OF PROMPT OUTPUT \n")

        if debug_mode:
            from langchain.schema import SystemMessage, HumanMessage
            messages_as_dict = [
                {
                    "role": "system" if isinstance(m, SystemMessage) else "human",
                    "content": m.content
                }
                for m in formatted_message
            ]
            with open("prompt.json", "w", encoding="utf-8") as f:
                json.dump(messages_as_dict, f, indent=4, ensure_ascii=False)
        
        
        response_stream = llm.stream(formatted_message)

        print(f"Response stream ended with entire response: {response_stream}")
        
        last_human_prompt = formatted_message[-1].content
        
        if debug_mode:
            messages_container.info(last_human_prompt)


        stream_thinking_container = None
        thought_expander = None
        # Display assistant response in chat message container
        if llm_option.name in supports_thought:
            thinking_container = messages_container.chat_message("assistant", avatar="💭")
            stream_thinking_container = thinking_container.empty()
            thought_expander = stream_thinking_container.expander("**Thinking...**")
        new_message_container = messages_container.chat_message("assistant")
        response_without_thinking = ""
        response_thinking = ""
        last_thought_topic = ""
        # response = st.write_stream(response_stream)
        # print(f"Response with entire response: {response}")
        stream_container = None
        # expanded_thoughts = False #control thoughts expansion during streaming

        for chunk in response_stream:
            print("Chunk type of: ", type(chunk))
            pprint.pprint(chunk)
            if isinstance(chunk, str):
                raise Exception("[Not Implemented, unsure if possible State to have multiple response_without_thinking]")
                new_message_container.write(chunk)
            elif isinstance(chunk, AIMessageChunk):
                content = chunk.content
                if isinstance(content, str):
                    if thought_expander != None:
                        # expand thought container --> final version of thoughts
                        thought_expander = stream_thinking_container.expander("**Thoughts...**")
                        thought_expander.write(response_thinking)
                        
                    if stream_container == None:
                        stream_container = new_message_container.empty()
                    response_without_thinking += content
                    stream_container.markdown(response_without_thinking)
                    # if response_without_thinking != None:
                    #     raise Exception("[UNKNOWN STATE, multiple responses without thinking]")
                elif isinstance(content, list):
                    for ai_message in content:
                        print("ai_message -->")
                        pprint.pprint(ai_message)
                        if ai_message["type"] == "thinking":
                            # extract bold part of the text
                            thought = ai_message["thinking"]
                            thought_topic = thought.splitlines()[0]
                            # stream_thinking_container.info(thought_topic)
                            thought_expander = stream_thinking_container.expander(thought_topic)
                            print("Thought:")
                            pprint.pprint(thought)
                            response_thinking += thought
                            thought_expander.write(response_thinking)
                            print("Response thinking: ")
                            pprint.pprint(response_thinking)
                            last_thought_topic = thought_topic
                        else:
                            raise Exception("[UNKNOWN STATE] Not sure which ai_messages are listed content here.")
                else:
                    raise Exception("[UNKNOWN STATE] Not implemented AIMessageChunk content can only be a list or str.")                
            else:
                raise Exception("[UNKNOWN STATE] The chunk can only be a string or a thinking chunk.")
        
        # st.session_state.expanded_thoughts = expanded_thoughts

        def convert_sources_to_interactive(text, document_sources):
            def findPage(document_sources, source_num):
                # debug_last_index = -1
                for document_source in document_sources:
                    # debug_last_index = document_source["source_index"]
                    # print(f"Debug index: {debug_last_index}")
                    print(f"Source_num ... :{source_num}")
                    if document_source["source_index"] == int(source_num):
                        return document_source
                
                messages_container.warning("Warning: could not find, source may be hallucinated!")
                
                print("Document_source: ", document_source)
                print(source_num)
                print(document_source["source_index"] == int(source_num))
                print(type(document_source["source_index"]))  # <class 'int'>
                print(type(source_num))
                print(f"[NOT FOUND] Document index: {source_num}")
                return {"page_content": "not_found"}
                # raise Exception("Could not find the page, something wrong with implementation")

            global popover_elements
            popover_elements = ""

            # add them as raw string as argument to popoverSource here (do not want to manage additional information)
            def replacer(match):
                global popover_elements
                # source_text = match.group(1)  # "Source 3"
                popover_target = ""
                source_numbers_group = match.group(2)   # "1, 2, 3, 5, 7, 9, 11, 12"
                print("source_numbers_group ...", source_numbers_group)
                source_numbers = [num.strip() for num in source_numbers_group.split(',')]
                print("source_numbers ...: ", source_numbers)

                for source_num in source_numbers:
                    if source_num == "":
                        continue
                    elif isinstance(source_num, str) and not source_num.isdigit():
                        print(f"Source was not an int: {source_num}, type: {type(source_num)}")
                        continue

                    document_source = findPage(document_sources, source_num)
                    
                    page_content = document_source["page_content"]
                    document_link = document_source["link"]

                    rand = random.randint(0, 10000)
                    query_id = document_source["query_id"]

                    # due to streamlit filtering out inline js when invoking container.html(), e.g. onclick listeners. The onclick listeners are attached seperately in an iframe component
                    page_content_with_button = page_content + f"""
                        <button id="pop-button-{query_id}-{rand}-{source_num}" data-document-link="{document_link}" style="
    display: block; padding-top: 0.3rem;
">View Source {document_source["source_index"]}</button>
    """

                    pprint.pprint(page_content_with_button)
                    # st-cf st-cg st-ch
                    # streamlit_popover_styling_classes = "st-bb st-es st-et st-eu st-ev st-ew st-ex st-fh st-b5 st-fi st-f0 st-f1 st-f2 st-f3 st-f4 st-f5 st-f6 st-f7 st-av st-aw st-ax st-ay st-f8 st-f9 st-fa st-fb st-az st-b0 st-b1 st-b2 st-fc st-fd st-fe st-ff"
                    streamlit_popover_styling_classes = ""

                    # need to convert markdown without triggering streamlit render, under the hood streamlit uses markdown-it-py
                    html_page_content = md.render(page_content_with_button)
                    popover_elements += f"""
                    <style>
                    [popovertarget="pop-{query_id}-{rand}-{source_num}"]{{
                        anchor-name: --pop-{query_id}-{rand}-{source_num};
                    }}

                    #pop-{query_id}-{rand}-{source_num} {{
                        top: anchor(--pop-{query_id}-{rand}-{source_num} bottom);
                        left: anchor(--pop-{query_id}-{rand}-{source_num} left);
                        transform: translateX(-50%);
                        max-width: 40%;
                        margin: 0;
                        overflow-y: scroll;
                    }}
                    </style>             
                    <div popover id="pop-{query_id}-{rand}-{source_num}" class="{streamlit_popover_styling_classes}">
                        <p>{html_page_content}</p>
                    </div>
                    """

                    print("Page_content: ")
                    print(type(page_content))
                    pprint.pprint(page_content)
                    
                    popover_target += f"""<span><button popovertarget="pop-{query_id}-{rand}-{source_num}">Source {source_num}</button></span>"""

                return popover_target

            pattern = r"(Source|Bron|Sources)\s((\d+,?\s?)+)"
            

            return re.sub(pattern, replacer, text), popover_elements
                    
        print(f"Response without thinking: {response_without_thinking}")
        sourced_response, popover_elements = convert_sources_to_interactive(response_without_thinking, document_sources)

        print("Popover elements: ", popover_elements)

        st.session_state.messages.append({"role": "assistant", "sources": document_sources, "content": sourced_response, "popover_elements": popover_elements, "thoughts": response_thinking})
        
        # force a rerun to update the sources.
        if not debug_mode:
            st.rerun()


