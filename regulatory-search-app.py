import streamlit as st
import os
from dotenv import load_dotenv

from langchain_core.prompts.chat import ChatPromptTemplate
import time

# from model_integrations import set_up_embedding_model, set_up_llm, load_vectorstore, Embedding_Model, Language_Model
# from model_integrations import Embedding_Model, Language_Model

import model_integrations

from enum import Enum
PERSIST_DIRECTORY = os.path.join("data", "vector_stores", "pension-martijn-embeddings")

class Embedding_Model(Enum):
    AZURE_TEXT_EMBEDDING_3_SMALL = {"display_name": "openai-text-embedding-3-small-v1", "model":"text-embedding-3-small", "data-ingestion-pipeline": "v1", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION", "persist_directory": PERSIST_DIRECTORY}
    AZURE_TEXT_EMBEDDING_3_SMALL_V2 = {"display_name": "openai-text-embedding-3-small+data-ingestion-v2.1", "data-ingestion-pipeline": "v2", "model":"text-embedding-3-small", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_V2.1", "persist_directory": PERSIST_DIRECTORY}
    # GEMINI_EMBEDDING_EXP_03_07 = {"model": "gemini-embedding-exp-03-07", "collection_name": "DATA_QUALITY_PENSION_GEMINI_EXP", "persist_directory": PERSIST_DIRECTORY}
    GEMINI_TEXT_EMBEDDING_004 = {"display_name": "gemini-text-embedding-004", "model": "text-embedding-004", "data-ingestion-pipeline": "v1", "collection_name": "DATA_QUALITY_PENSION_GEMINI", "persist_directory": PERSIST_DIRECTORY}

class Language_Model(Enum):
    AZURE_GPT_4O_MINI = {"model": "gpt-4o-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "temperature": 0.2}
    AZURE_OPENAI_O4_MINI = {"model": "o4-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT_SWEDEN"], "api_key": os.environ["AZURE_OPENAI_API_KEY_SWEDEN"]}
    GEMINI_25_PRO_EXP = {"model": "gemini-2.5-pro-exp-03-25"}

print(f"Loading environment, libraries, and resources...")

load_start_time = time.time()

# load environment variables
load_dotenv()


# set up user configuration options
with st.sidebar:
    st.title("User Config")
    embedding_model_option = st.selectbox(
        "Which embedding model to choose",
        (Embedding_Model.AZURE_TEXT_EMBEDDING_3_SMALL, Embedding_Model.AZURE_TEXT_EMBEDDING_3_SMALL_V2, Embedding_Model.GEMINI_TEXT_EMBEDDING_004),
        format_func=lambda x: x.value["display_name"]
    )
    llm_option = st.selectbox(
    "Which LLM to choose",
    (Language_Model.AZURE_GPT_4O_MINI, Language_Model.GEMINI_25_PRO_EXP, Language_Model.AZURE_OPENAI_O4_MINI),
    format_func=lambda x: x.value["model"]
    )
    k = st.slider("Pieces of text retrieved", 0, 10, 2)

    st.title("Debugger")
    debug_mode = st.toggle(
        "Debug Mode",
        True
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

st.title("💬 Regulation Search")
st.caption("🚀 Powererd by Triple A")

generation_instructions = """
Zoekassistent t.b.v. Datakwaliteit binnen de Wtp-context:
Je bent een juridische en beleidsmatige zoekassistent, gespecialiseerd in regelgeving, beleidsdocumenten en handreikingen rondom de Wet toekomst pensioenen (Wtp). Je helpt gebruikers bij het vinden en interpreteren van informatie met betrekking tot datakwaliteit binnen dit wettelijke kader.
     
Context:

* De Wet toekomst pensioenen (Wtp) is sinds 1 juli 2023 van kracht.
* Een belangrijk onderdeel van de wet is het waarborgen van correcte, volledige en tijdige data.
* Pensioenuitvoerders, verzekeraars en administrateurs zijn verantwoordelijk voor het verbeteren en monitoren van datakwaliteit.
* Toezichthouders zoals DNB en AFM hebben handreikingen en eisen geformuleerd met betrekking tot datakwaliteit.

Jouw taak:
* Help gebruikers bij het vinden van relevante bronnen (wetten, besluiten, beleidsdocumenten, toezichtsregels, handreikingen).
* Geef korte, accurate toelichtingen op gevonden documenten of regels.
* Wijs indien mogelijk op gerelateerde wetgeving zoals de Pensioenwet, Wet op het financieel toezicht (Wft), AVG (m.b.t. gegevensverwerking), of ESMA/EIOPA-richtlijnen.
* Geef bij een zoekvraag altijd een korte samenvatting van de meest relevante resultaten, met bronverwijzing (indien mogelijk).
* Indien de gebruiker termen gebruikt als 'datakwaliteitseisen', 'verantwoordingsdocument', of 'transitie-uitvraag', verbind deze dan met Wtp-context en de rol van toezichthouders of pensioenuitvoerders.

Voorbeeld van een gebruikersvraag:
Vraag: Welke eisen stelt DNB aan datakwaliteit bij de overgang naar het nieuwe pensioenstelsel?

Gewenste reactie van het model o.b.v. prompt:

De Nederlandsche Bank (DNB) stelt dat pensioenuitvoerders bij de transitie naar het nieuwe stelsel moeten kunnen aantonen dat hun data juist, volledig en tijdig is. In de leidraad 'Datakwaliteit bij de transitie naar het nieuwe pensioenstelsel' van juni 2023 staan o.a. eisen rondom datavalidatie, verantwoording richting deelnemers en interne audit. Zie ook de beleidsuitingen van DNB over datakwaliteit op hun website.

Bron: Pensioen Federatie - https://www.pensioenfederatie.nl/website/publicaties/servicedocumenten/kader-datakwaliteit
"""
# NOT IN USE YET, CAN BE USEFUL FOR VERIFICATION
#source: https://docs.llamaindex.ai/en/stable/examples/workflow/citation_query_engine/
citation_instructions = """
Please answer the following question using only the information provided in the numbered sources below. When you reference information from a source, cite the corresponding source number(s) in brackets (e.g., [1]). Every answer must include at least one citation, but you should only cite a source if you are explicitly referencing it. If none of the sources are relevant or helpful, clearly state that in your response.

Example
Source 1:
The sky is red in the evening and blue in the morning.
Source 2:
Water is wet when the sky is red.
Query: When is water wet?
Answer: Water will be wet when the sky is red [2], which occurs in the evening [1].

Now it's your turn. Below are several numbered sources of information:

"\n------\n"
"{context_str}"
"\n------\n"
"Query: {query_str}\n"
"Answer: "
"""

system_instructions_dict = {"role": "system", "content": generation_instructions}

if "messages" not in st.session_state:
    # chat prompt generated with GPT-4o https://chatgpt.com/share/6800c49f-a2fc-800f-920a-8defd32dc16d
    st.session_state["messages"] = [
    system_instructions_dict,
]
    
st.chat_message("assistant").write("Hello I am here to help you search through documents")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input():
    model_name = llm.__dict__.get("model_name") or llm.__dict__.get("model").split("models/")[1] #model name stored somewhere different depending on Azure or Google integration of Langchain
    if debug_mode:
        st.info(model_name)
    print(f"Running query with model: {model_name}")
    if llm_option.value["model"] != model_name:
        raise Exception(f"Option not respected, running {model_name}, while expecting {llm_option.value["model"]}")
    if debug_mode:
        st.info(f"Running query with model: {model_name}")
    print(query)
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    matched_documents = vectorstore.similarity_search(query=query,k=k)

    print(f"First documents of all matched documents: {matched_documents[0].__dict__}")
    
    chunks_concatenated = ""
    document_sources = []
    if embedding_model_option.value["data-ingestion-pipeline"] == "v1":
        for idx, document in enumerate(matched_documents):
            source = f"{document.metadata["source"]} on page {document.metadata["page_label"]}"
            #note: unsure why metadata has a page and page_label attribute?, verified that page_label was correct for data kwality pdf
            document_sources.append(source)
            chunks_concatenated += f"\nsource {idx}, ref {source}:\n\n {document.page_content} \n\n\n"
    elif embedding_model_option.value["data-ingestion-pipeline"] == "v2":
        for idx, chunk in enumerate(matched_documents):
            headers = []
            for key, value in chunk.metadata.items():
                header = ": ".join([key, value])
                headers.append(header)
            source = f"{"\n".join(headers)}"
            # print(f"SOURCE FOR {idx}: {source}")
            # quick fix end of page is causing formatting issues by interpreting as h2
            # but in the normal .md the appropriate newlines are there, not sure where the newlines
            # are removed, likely not within my implementation, could when loading in the vectorstore or by here
            # saw that already multiple people were complaining of not respecting newline with langchain implementation of markdownheader split

            # page_content_2 = chunk.page_content.replace("-----", "")
            # print(f"PAGE CONTEXT FOR {idx}: {chunk.page_content}")
            chunks_concatenated += f"\nsource {idx}, ref {source}:\n\n {chunk.page_content} \n\n\n"
    else:
        raise Exception("Way of displaying metadata from data ingestion pipeline not implemented")

    print(f"CHUNKS CONCATENATED FOR {idx}: {chunks_concatenated}")
    print(f"DOCUMENT SOURCE: {document_sources}")
    # print(prompt)

    prompt = f"""
    {chunks_concatenated}
    Based on the above mentioned sources, can you provide an answer on the following question?
    Question: {query}
    Answer: 
    """
    
    template = ChatPromptTemplate([("system", generation_instructions) , ("user", prompt)])
    
    print(f"PROMPT FOR LLM: \n\n {template} \n\n END OF PROMPT OUTPUT \n")

    response_stream = llm.stream(template.format_messages())

    # result_text = ""
    # for matched_document in matched_documents:
    #     result_text += matched_document.page_content


    matched_documents_message = f"""
    {len(matched_documents)} chunks(s) matched: \n
    {chunks_concatenated}"""
    st.info(matched_documents_message)

    if debug_mode: #save in session state
        st.session_state.messages.append({"role": "info", "content": ":blue-badge[Info]"
+ matched_documents_message})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_stream)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})