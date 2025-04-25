import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_chroma import Chroma
import time
from enum import Enum

load_start_time = time.time()

# load environment variables
load_dotenv()

PERSIST_DIRECTORY = os.path.join("vector_stores", "pension-martijn-embeddings")

# define configuration options
class Embedding_Model(Enum):
    AZURE_TEXT_EMBEDDING_3_SMALL = {"model":"text-embedding-3-small", "collection_name": "DATA_QUALITY_PENSION", "persist_directory": PERSIST_DIRECTORY}
    # GEMINI_EMBEDDING_EXP_03_07 = {"model": "gemini-embedding-exp-03-07", "collection_name": "DATA_QUALITY_PENSION_GEMINI_EXP", "persist_directory": PERSIST_DIRECTORY}
    GEMINI_TEXT_EMBEDDING_004 = {"model": "text-embedding-004", "collection_name": "DATA_QUALITY_PENSION_GEMINI", "persist_directory": PERSIST_DIRECTORY}

class Language_Model(Enum):
    AZURE_GPT_4O_MINI = {"model": "gpt-4o-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "temperature": 0.2}
    AZURE_OPENAI_O4_MINI = {"model": "o4-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT_SWEDEN"], "api_key": os.environ["AZURE_OPENAI_API_KEY_SWEDEN"]}
    GEMINI_25_PRO_EXP = {"model": "gemini-2.5-pro-exp-03-25"}

# load models and vectorstore
# cached becuase streamlit reloads file on save
@st.cache_resource
def create_azure_embedding_model(model):
    print("HI")
    embedding_model = AzureOpenAIEmbeddings(
        model=model,
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version="2023-05-15",
        api_key=os.environ["AZURE_OPENAI_API_KEY"]
    )
    return embedding_model

@st.cache_resource
def create_gemini_embedding_model(model):
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}", 
        google_api_key=os.environ["GOOGLE_API_KEY"]
    )

@st.cache_resource
def create_azure_llm(model_options: Language_Model):
    # based on https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#list---assistants
    # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    # We generally recommend altering this or top_p but not both.
    # defaults to 1

    # default to 1 as reasoning model do not support temperature other than 1
    #https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/reasoning?tabs=python-secure%2Cpy
    # Not Supported
    # The following are currently unsupported with reasoning models:
    # temperature, top_p, presence_penalty, frequency_penalty, logprobs, top_logprobs, logit_bias, max_tokens
    temperature = 1
    if "temperature" in model_options.value:
        print("SETTING TEMPERATURE FOR MODEL, PLEASE NOT FOR O series" \
        " Only the default (1) value is supported.")
        temperature = model_options.value["temperature"]


    print("temperature setting is changed")
    endpoint = model_options.value["api_endpoint"] #or os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = model_options.value["api_key"] #or os.environ["AZURE_OPENAI_API_KEY"]
    return AzureChatOpenAI(
        model=model_options.value["model"],
        azure_endpoint=endpoint,
        api_version="2025-01-01-preview",
        api_key=api_key,
        temperature=temperature
    )

@st.cache_resource
def create_gemini_llm(model):
    return ChatGoogleGenerativeAI(
        model=model, 
        api_key=os.getenv("GOOGLE_API_KEY"), 
        temperature=0.2
    )

@st.cache_resource
def load_vectorstore(model_option: Embedding_Model):
    # load the vectorstore
    print("LOADING VECTOR STORE...")
    embedding_model = set_up_embedding_model(embedding_model_option)
    vectorstore = Chroma(model_option.value["collection_name"], embedding_model, model_option.value["persist_directory"])
    print(f"Vectorstore loaded in with count: {vectorstore._collection.count()}")
    return vectorstore

def set_up_llm(model_option: Language_Model):
    llm = None
    if model_option.name.startswith("AZURE"):
        llm = create_azure_llm(model_option)
    elif model_option.name.startswith("GEMINI"):
        llm = create_gemini_llm(model_option.value["model"])
    else:
        raise Exception("Unknown model")
    return llm

def set_up_embedding_model(model_option: Embedding_Model):
    embedding_model = None
    if model_option.name.startswith("AZURE"):
        embedding_model = create_azure_embedding_model(model_option.value["model"])
    elif model_option.name.startswith("GEMINI"):
        embedding_model = create_gemini_embedding_model(model_option.value["model"])
    else:
        raise Exception("Unknown model")
    return embedding_model


load_elapsed_time = time.time() - load_start_time
print(f"Elapsed time for loading libraries and vector database: {load_elapsed_time}s")

# set up user configuration options
with st.sidebar:
    st.title("User Config")
    embedding_model_option = st.selectbox(
        "Which embedding model to choose",
        (Embedding_Model.AZURE_TEXT_EMBEDDING_3_SMALL, Embedding_Model.GEMINI_TEXT_EMBEDDING_004),
        format_func=lambda x: x.value["model"]
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

embedding_model = set_up_embedding_model(embedding_model_option)
llm = set_up_llm(llm_option)
vectorstore = load_vectorstore(embedding_model_option)

print(f"""CURRENT CONFIG:
llm {type(llm)}
embedding {type(embedding_model)}
debug {debug_mode}
\n
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
    st.info(llm.__dict__)
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
    for idx, document in enumerate(matched_documents):
        source = f"{document.metadata["source"]} on page {document.metadata["page_label"]}"
        #note: unsure why metadata has a page and page_label attribute?, verified that page_label was correct for data kwality pdf
        document_sources.append(source)
        chunks_concatenated += f"\nsource {idx}, ref {source}:\n\n {document.page_content} \n\n\n"

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