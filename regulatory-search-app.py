import streamlit as st
from dotenv import load_dotenv
import pprint
import json

from langchain_core.prompts.chat import ChatPromptTemplate
import time

print(f"Loading environment, libraries, and resources...")

load_start_time = time.time()

# load environment variables
load_dotenv()
import os

import model_integrations
from model_config import Embedding_Model, Language_Model

st.set_page_config(layout='wide')

st.markdown("""
    <style>
        /* This targets the block containing the columns */
        [data-testid="stVerticalBlockBorderWrapper"]:nth-last-child(1) {
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
            }
    </style>
""", unsafe_allow_html=True)


# set up user configuration options
with st.sidebar:
    st.title("User Config")
    embedding_model_option = st.selectbox(
        "Which embedding model to choose",
        (Embedding_Model.QWEN_3_EMBEDDING_SOLVENCY_II, Embedding_Model.GEMINI_EMBEDDING_001_SOLVENCY_II),
        format_func=lambda x: x.value["display_name"]
    )
    llm_option = st.selectbox(
    "Which LLM to choose",
    (Language_Model.GEMINI_25_PRO, Language_Model.AZURE_GPT_4O_MINI , Language_Model.AZURE_OPENAI_O4_MINI),
    format_func=lambda x: x.value["model"]
    )
    k = st.slider("Pieces of text retrieved", 0, 10, 5)

    st.title("Debugger")
    debug_mode = st.toggle(
        "Debug Mode",
        False
    )

@st.cache_resource
def cached_embedding_model(embedding_model_option: Embedding_Model):
    return model_integrations.set_up_embedding_model(embedding_model_option)

@st.cache_resource
def cached_llm(llm_option: Language_Model):
    return model_integrations.set_up_llm(llm_option)

@st.cache_resource
def cached_vectorstore(embedding_model_option):
    return model_integrations.load_vectorstore(embedding_model_option)

# load models and vectorstore
# cached because streamlit reloads after each user input
embedding_model = cached_embedding_model(embedding_model_option)
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



# generation_instructions = """
# Zoekassistent t.b.v. Datakwaliteit binnen de Wtp-context:
# Je bent een juridische en beleidsmatige zoekassistent, gespecialiseerd in regelgeving, beleidsdocumenten en handreikingen rondom de Wet toekomst pensioenen (Wtp). Je helpt gebruikers bij het vinden en interpreteren van informatie met betrekking tot datakwaliteit binnen dit wettelijke kader.
     
# Context:

# * De Wet toekomst pensioenen (Wtp) is sinds 1 juli 2023 van kracht.
# * Een belangrijk onderdeel van de wet is het waarborgen van correcte, volledige en tijdige data.
# * Pensioenuitvoerders, verzekeraars en administrateurs zijn verantwoordelijk voor het verbeteren en monitoren van datakwaliteit.
# * Toezichthouders zoals DNB en AFM hebben handreikingen en eisen geformuleerd met betrekking tot datakwaliteit.

# Jouw taak:
# * Help gebruikers bij het vinden van relevante bronnen (wetten, besluiten, beleidsdocumenten, toezichtsregels, handreikingen).
# * Geef korte, accurate toelichtingen op gevonden documenten of regels.
# * Wijs indien mogelijk op gerelateerde wetgeving zoals de Pensioenwet, Wet op het financieel toezicht (Wft), AVG (m.b.t. gegevensverwerking), of ESMA/EIOPA-richtlijnen.
# * Geef bij een zoekvraag altijd een korte samenvatting van de meest relevante resultaten, met bronverwijzing (indien mogelijk).
# * Indien de gebruiker termen gebruikt als 'datakwaliteitseisen', 'verantwoordingsdocument', of 'transitie-uitvraag', verbind deze dan met Wtp-context en de rol van toezichthouders of pensioenuitvoerders.

# Voorbeeld van een gebruikersvraag:
# Vraag: Welke eisen stelt DNB aan datakwaliteit bij de overgang naar het nieuwe pensioenstelsel?

# Gewenste reactie van het model o.b.v. prompt:

# De Nederlandsche Bank (DNB) stelt dat pensioenuitvoerders bij de transitie naar het nieuwe stelsel moeten kunnen aantonen dat hun data juist, volledig en tijdig is. In de leidraad 'Datakwaliteit bij de transitie naar het nieuwe pensioenstelsel' van juni 2023 staan o.a. eisen rondom datavalidatie, verantwoording richting deelnemers en interne audit. Zie ook de beleidsuitingen van DNB over datakwaliteit op hun website.

# Bron: Pensioen Federatie - https://www.pensioenfederatie.nl/website/publicaties/servicedocumenten/kader-datakwaliteit
# """
def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# NOT IN USE YET, CAN BE USEFUL FOR VERIFICATION
#source: https://docs.llamaindex.ai/en/stable/examples/workflow/citation_query_engine/
# citation_instructions = """
# Please answer the following question using only the information provided in the numbered sources below. When you reference information from a source, cite the corresponding source number(s) in brackets (e.g., [1]). Every answer must include at least one citation, but you should only cite a source if you are explicitly referencing it. If none of the sources are relevant or helpful, clearly state that in your response.

# Example
# Source 1:
# The sky is red in the evening and blue in the morning.
# Source 2:
# Water is wet when the sky is red.
# Query: When is water wet?
# Answer: Water will be wet when the sky is red [2], which occurs in the evening [1].

# Now it's your turn. Below are several numbered sources of information:

# "\n------\n"
# "{context_str}"
# "\n------\n"
# "Query: {query_str}\n"
# "Answer: "
# """
generation_instructions = load_prompt("prompt/solvency_II_instructions.md")
system_instructions_dict = {"role": "system", "content": generation_instructions}

if 'pdf_to_display' not in st.session_state:
    st.session_state.pdf_to_display = None

if "messages" not in st.session_state:
    # chat prompt generated with GPT-4o https://chatgpt.com/share/6800c49f-a2fc-800f-920a-8defd32dc16d
    st.session_state["messages"] = [
    system_instructions_dict,
]

def displayPDF(file_name):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join("app", "static")
    ALLOWED_PDF_DIR = os.path.join(APP_ROOT, STATIC_DIR)

    real_file_path = os.path.join(ALLOWED_PDF_DIR, file_name)

    print(f"Real file path: {real_file_path}")

    if not os.path.realpath(real_file_path).startswith(os.path.realpath(ALLOWED_PDF_DIR)):
        raise Exception("Path not allowed, only serves PDF from static folder ", ALLOWED_PDF_DIR)
    
    secure_file_path = os.path.join(STATIC_DIR, file_name)

    # Opening file from file path
    # with open(secure_file_path, "rb") as f:
    #     base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # # Embedding PDF in HTML
    # pdf_display =  f"""<embed
    # class="pdfobject"
    # type="application/pdf"
    # title="Embedded PDF"
    # src="data:application/pdf;base64,{base64_pdf}"
    # style="overflow: auto; width: 100%; height: 100%;">"""
    # pdf_url = f"{secure_file_path}"
    # pdf_url = os.path.join("app", "static", "solvency-II-files", "Master_Thesis (7).pdf", "#page=3")

    print("Displaying pdf with: ", secure_file_path)
    pdf_display = f'<iframe id=pdf_sidebar src="{secure_file_path}" width="700" height="550" type="application/pdf"></iframe>'
    
    # Displaying File
    with pdf_col:
        st.button(key="close-button", label="close", on_click=lambda: setattr(st.session_state, 'pdf_to_display', None), icon="❌")
        st.markdown(pdf_display, unsafe_allow_html=True)

    

with st.container():
    chat_col, pdf_col = st.columns([1, 1])
        
        
# <button popovertargetaction="hide" popovertarget="pop-1">Close</button>
    with chat_col:
        st.title("💬 Regulation Search")
        st.caption("🚀 Powererd by Triple A")
        file_name = r"Master_Thesis-small.pdf" #replace once metadata of documents are available.

    if st.session_state.pdf_to_display:
        print("pdf: ", st.session_state.pdf_to_display)
        displayPDF(st.session_state.pdf_to_display)

    # not sure why this needs to be seperate, but if in main call of chat_col the layout does not work.
    # with chat_col:
        

    # test_pdf_url = os.path.join("../", "cat.png")
    # pdf_url = test_pdf_url

    import random

    def set_pdf_to_display(pdf_link):
        # lambda: setattr(st.session_state, 'pdf_to_display', document_link)
        st.session_state.pdf_to_display = pdf_link


    def displaySources(document_sources):
        added_sources = []
        
        deduplicated_document_sources = []
        for document_source in document_sources:
            if document_source["link"] not in added_sources:
                # check if title is not set in metadata
                # print(f"Title: used {title}")
                
                added_sources.append(document_source["link"])
                deduplicated_document_sources.append(document_source)
        
        
        container_key = f"sources-buttons-container-{deduplicated_document_sources[0]["query"]}".replace(" ", "-")
        
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
                    args = (document_link, )
                    print("Args: ", args)

                    print(f"Document link: {document_source["link"]}")
                    st.button(
                        key=f"{document_source["query"]}---{document_source["link"]}",
                        label=f"{document_source["title"]}", 
                        on_click= set_pdf_to_display, 
                        args=args,
                        icon="🔗"
                    )

    with chat_col:
        messages_container = st.container()
        messages_container.chat_message("assistant").write("Hello I am here to help search through documents related to Solvency II")
        for message in st.session_state.messages:
            # do not print out system prompt
            if message["role"] == "system":
                 continue
            
            with messages_container.chat_message(message["role"]):
                if "sources" in message:
                    with messages_container: 
                        displaySources(message["sources"])

                if "style" in message:
                    messages_container.html(message["style"])
                messages_container.markdown(message["content"], unsafe_allow_html=True)

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

            matched_documents = vectorstore.similarity_search(query=query,k=k)

            print(f"First documents of all matched documents: {matched_documents[0].__dict__}")
            
            chunks_concatenated = ""
            document_sources = []
            if embedding_model_option.value["data-ingestion-pipeline"] == "v1":
                for idx, document in enumerate(matched_documents):
                    source = f"{document.metadata["source"]} on page {document.metadata["page_label"]}"
                    #note: unsure why metadata has a page and page_label attribute?, verified that page_label was correct for data kwality pdf
                    document_sources.append(source)
                    chunks_concatenated += f"###\n source {idx}, ref {source}:\n\n {document.page_content} \n\n\n"
            elif embedding_model_option.value["data-ingestion-pipeline"] == "v2":
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

                    # headers = []
                    # # print("chunk metadata: ", chunk)
                    # for key, value in chunk.metadata.items():
                    #     header = ": ".join([str(key), str(value)])
                    #     headers.append(header)
                    # source = f"{"\n".join(headers)}"



                    # deduplicated list of document sources, used at end of chat
                    print(f"chunk metadata: source {chunk.metadata["source"]}")

                    
                    # example: chunk.metadata["source"] == data\raw\solvency-II-files\solvency II - level 2.pdf

                    print(f"split: {str(chunk.metadata["source"]).split("data\\raw\\")}")

                    document_source = {
                            "source_index": source_index,
                            "link": str(chunk.metadata["source"]).split("data\\raw\\")[-1],
                            "title": title,
                            "page_content": chunk.page_content,
                            "query": query
                        }

                    document_sources.append(document_source)
                    # if chunk.metadata["source"] not in added_sources:
                    #     # check if title is not set in metadata

                    #     print(f"Title: used {title}")

                        
                    #     added_sources.append(chunk.metadata["source"])
                    
                    # used to debug
                    chunks_concatenated += f"\n ### source {source_index} \n\n metadata:\n {source_metadata}:\n\n extract:\n\n {chunk.page_content} \n\n\n"
            else:
                raise Exception("Way of displaying metadata from data ingestion pipeline not implemented")


            print(f"CHUNKS CONCATENATED FOR {source_index}: {chunks_concatenated}")
            print(f"DOCUMENT SOURCE: {document_sources}")

            prompt = f"""
            ## Question
            \n\n {query} \n\n
            \n## Context
            \n\n {chunks_concatenated} \n\n
            \n## Answer
            \n\n When answering reference ONLY if applicable source with (Source <insert number>). Answer based on the mentioned sources in the Context answer the Question. 
            \n\n
            """

            # if debug_mode:
            #     messages_container.chat_message("assistant").write(document_sources)

            # add sources to session state
            print(f"Document sources: {document_sources}")

            with messages_container:
                displaySources(document_sources)

            st.session_state.messages.append({"role": "user", "content": query, "sources": document_sources})

            
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

            # matched_documents_message = f"""
            # {len(matched_documents)} chunks(s) matched: \n
            # {chunks_concatenated}"""

            # if debug_mode:
            #     messages_container.info(matched_documents_message)
            
            last_human_prompt = formatted_message[-1].content
            
            if debug_mode:
                messages_container.info(last_human_prompt)


        #     if debug_mode: #save in session state
        #         st.session_state.messages.append({"role": "info", "content": ":blue-badge[Info]"
        # + matched_documents_message})

            # Display assistant response in chat message container
            with messages_container.chat_message("assistant"):
                response = st.write_stream(response_stream)
                print(f"Response stream ended with entire resposne: {response}")
            # Add assistant response to chat history

            # text = "Based on the provided sources, Solvency II is the common name for Directive 2009/138/EC of the European Parliament and of the Council of 25 November 2009 (Source 3, Source 2)"

            import re
            import random

            def convert_sources_to_interactive(text, document_sources):
                def findPage(document_sources, source_num):
                    debug_last_index = -1
                    for document_source in document_sources:
                        debug_last_index = document_source["source_index"]
                        print(f"Debug index: {debug_last_index}")
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

                global styling_popover_elements
                styling_popover_elements = ""
                
                # add them as raw string as argument to popoverSource here (do not want to manage additional information)
                def replacer(match):
                    global styling_popover_elements
                    source_text = match.group(1)  # "Source 3"
                    source_num = match.group(2)   # "3"

                    document_source = findPage(document_sources, source_num)
                    
                    page_content = document_source["page_content"]

                    rand = random.randint(0, 10000)
                    fake_query_id = "test" #Failing on styling, it is opening though?, may be special characters interpreted differently by css and html: document_source["query"][:20].replace(" ", "-")

                    styling_popover_elements += f"""
                    <style>
                    [popovertarget="pop-{fake_query_id}-{rand}-{source_num}"]{{
                        anchor-name: --pop-{fake_query_id}-{rand}-{source_num};
                    }}

                    #pop-{fake_query_id}-{rand}-{source_num} {{
                        top: anchor(--pop-{fake_query_id}-{rand}-{source_num} bottom);
                        left: anchor(--pop-{fake_query_id}-{rand}-{source_num} center);
                        margin: 0;
                    }}
                    </style>                    
                    """

                    print("Page_content: ")
                    print(type(page_content))
                    pprint.pprint(page_content)

                    page_content = page_content.replace("\n", " ") # need to do as otherwise the page_content gets interpretted as seperate elements
                    # and then they for some reason are not included in the popover.
                    # hack for now.

                    popover_element = f"""<div popover id="pop-{fake_query_id}-{rand}-{source_num}">
                        <p>{page_content}</p>
                    </div><button popovertarget="pop-{fake_query_id}-{rand}-{source_num}">Link {source_num}</button>"""


                                        # find text related to the sources.
                    # popover_element = f"{source_text}"

                    # return f'<button class="popover" onclick="popoverSource({source_num})" onmouseover="popoverSource({source_num})">{source_text}</button>'
                    return popover_element

                pattern = r"(Source\s(\d+))"
                return re.sub(pattern, replacer, text), styling_popover_elements
            
            sourced_response, styling_popover_element = convert_sources_to_interactive(response, document_sources)
            # st.markdown(sourced_response, unsafe_allow_html=True)

            print("Styling Popover: ", styling_popover_element)

            st.session_state.messages.append({"role": "assistant", "content": sourced_response, "style": styling_popover_element})

# st.html("""
# <script>
#             const popoverSource = (source_num) => {
#                 console.log("hi, there you")
#                 alert("Hi there: ", source_num)
#             }
# </script>
# """)