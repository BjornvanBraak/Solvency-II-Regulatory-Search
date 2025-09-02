from langchain_chroma import Chroma
import streamlit as st
from markdown_it import MarkdownIt
# from markdown_it_py import MarkdownIt #internally streamlit uses this as well, potential dependency conflict, be aware.
md = MarkdownIt()
md.enable('table')

from dotenv import load_dotenv
import json
import os
import re
import uuid
import pickle

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.messages.ai import AIMessageChunk
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever

from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore

import time
import streamlit.components.v1 as components

from openai import RateLimitError as OpenAIRateLimitError

from open_pdf_button import my_component

print(f"[INFO] Loading environment, libraries, and resources...")

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
            height: calc(100vh - 96px - 30px);
        }
        .st-key-pdf-display-container .stElementContainer:has(iframe) {
            flex: 1;   
        }
            
        .st-key-pdf-display-container .stElementContainer:has(iframe) * {
            width: 100%;
            height: 100%;
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
                border-bottom-color: rgba(49, 51, 63, 0.2);
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
    <style>
            .st-key-footer-container {
                position: absolute;
                bottom: -1500px;
            }
    </style>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            font-family: sans-serif;
        }

        th, td {
            border: 1px solid #dddddd;
            text-align: center;
            padding: 8px;
        }
        
        tr {
            background-color: white;
        }

        tr:nth-child(even) {
            background-color: rgba(242, 242, 242, 0.5);
        }

        th {
            background-color: #0073AB;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)


# will be removed in later version, temporary support.
def get_short_title(filename: str):
    filename_to_short_title = {
    "Consolidated_GLs_CBs_ET_EN.pdf": "CB Guidelines (Consolidated)",
    "EIOPA-BoS-14-259_Final report_ORSA.pdf": "ORSA Final Report",
    "Guidelines on basis risk.pdf": "Basis Risk Guidelines",
    "Guidelines on Classification of Own Funds.pdf": "Own Funds Classification",
    "Guidelines on group solvency.pdf": "Group Solvency Guidelines",
    "Guidelines on health catastrophe risk sub-module.pdf": "Health Cat Risk Guidelines",
    "Guidelines on look-through approach.pdf": "Look-through Approach",
    "Guidelines on operational functioning of colleges.pdf": "Colleges Operational Guidelines",
    "Guidelines on Own Risk Solvency Assessment .pdf": "ORSA Guidelines",
    "Guidelines on reporting and public disclosure.pdf": "Reporting & Disclosure Guidelines",
    "Guidelines on ring-fenced funds.pdf": "Ring-fenced Funds Guidelines",
    "Guidelines on supervisory review process.pdf": "Supervisory Review Guidelines",
    "Guidelines on the use of internal models.pdf": "Internal Models Guidelines",
    "Guidelines on undertaking-specific parameters.pdf": "USP Guidelines",
    "JC 2024-34_Guidelines on costs and losses_DORA.pdf": "DORA Costs & Losses Guidelines",
    "Joint ESA Final Report on Art 97 Guidelines MiCAR.pdf": "MiCAR Art. 97 Final Report",
    "Joint ESA Gls MiCAR %28JC 2024 28%29_EN.pdf": "MiCAR Joint Guidelines (JC 2024/28)",
    "Joint Guidelines on Risk Factors.pdf": "Risk Factors Guidelines",
    "Privacy Statement - ESAs Information System.pdf": "ESA Privacy Statement",
    "Revised Guidelines on Contract Boundaries.pdf": "CB Guidelines (Revised)",
    "Technical Annexes.pdf": "Technical Annexes",
    "solvency II - level 1 - v2.pdf": "Solvency II – Level 1 Directive",
    "solvency II - level 2.pdf": "Solvency II – Level 2 Regulation"
    }
    if not filename in filename_to_short_title:
        print(f"[Warning] No short title found for {filename}")
        return filename
    
    return filename_to_short_title[filename]
    




supports_thought = ["GEMINI_25_PRO"]

sidebar = st.sidebar

sidebar.header("Config")
# order changed back, bug in upgraded version of Embedding_Model.GEMINI_EMBEDDING_001
embedding_model_option = sidebar.selectbox(
    "Which embedding model to choose",
    (Embedding_Model.AZURE_TEXT_EMBEDDING_3_LARGE_SOLVENCY_V3, Embedding_Model.AZURE_TEXT_EMBEDDING_3_LARGE_SOLVENCY_V2, Embedding_Model.QWEN_3_EMBEDDING_SOLVENCY_II_V2, Embedding_Model.GEMINI_EMBEDDING_001_SOLVENCY_II),
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
    (Language_Model.AZURE_GPT_5, Language_Model.AZURE_GPT_4O_MINI, Language_Model.GEMINI_25_PRO, Language_Model.AZURE_OPENAI_O4_MINI, Language_Model.GROK_4),
    format_func=lambda x: x.value["model"]
)
k = sidebar.slider("Pieces of text retrieved (k)", 0, 20, 10)
top_n = sidebar.slider("Filtered after retrieved (max k)", 0, k, 5 if k >= 5 else k)

sidebar.header("Debugger")
debug_mode = sidebar.toggle(
    "Debug Mode",
    False
)

def count_tokens(text: str) -> int:
    """The number of tokens in a text string"""

    # naive approximation of the number of approximately 4 characters per token
    return len(text) / 4

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

def chroma_hasher(vectorstore) -> str:
    # Example: hash on collection name + persist path
    return f"{vectorstore._collection.name}"

@st.cache_resource(hash_funcs={Chroma: chroma_hasher})
def cached_retriever(embedding_model_option, vectorstore):
    if "doc_persist_directory" in embedding_model_option.value:
        # Multivector embedding
        # NOTE: ENTIRE DOCSTORE IS SAVED AS A PICKLE FILE FOR PROOF OF CONCEPT
        # loads in list(zip(chunk_ids, chunks))
        with open(os.path.join(embedding_model_option.value["doc_persist_directory"], embedding_model_option.value["collection_name"] + ".pkl"), "rb") as f:
            doc_store = pickle.load(f)

        byte_store = InMemoryByteStore()
        id_key = embedding_model_option.value["foreign_key_id"]

        retriever = MultiVectorRetriever(
            vectorstore=vectorstore,
            byte_store=byte_store,
            id_key=id_key,
        )

        # load docstore into memory
        retriever.docstore.mset(doc_store)
        return retriever
    else:
        return vectorstore.as_retriever(search_kwargs={"k": k})

# load models and vectorstore
# cached because streamlit reloads after each user input
embedding_model = cached_embedding_model(embedding_model_option)
reranker_model = cached_reranker_model(reranker_model_option, top_n)
llm = cached_llm(llm_option)
vectorstore = cached_vectorstore(embedding_model_option)
retriever = cached_retriever(embedding_model_option, vectorstore)

load_elapsed_time = time.time() - load_start_time
print(f"[INFO]Elapsed time for loading libraries and vector database: {load_elapsed_time}s")

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
# if "document_link_through_link" not in st.session_state:
#     st.session_state["document_link_through_link"] = None

if 'pdf_to_display' not in st.session_state:
    st.session_state.pdf_to_display = None

if 'pdf_page_number' not in st.session_state:
    st.session_state.pdf_page_number = None

if 'pdf_cache_bust' not in st.session_state:
    st.session_state.pdf_cache_bust = uuid.uuid4()

if 'prev_pdf_for_cache_bust' not in st.session_state:
    st.session_state.prev_pdf_for_cache_bust = None

if 'prev_page_number' not in st.session_state:
    st.session_state.prev_page_number = None

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
    # st.session_state.pdf_to_display = None
    # st.session_state.pdf_page_number = None
    # print("PDF display closed.")
    print(f"[close_pdf_display] Closing PDF display, setting pdf_to_display to None")
    # not sure why I need a message_id, because popover does not update .message_to_component, so if you first clear_pdf via displaySources button, and thereafter use popover sources, the .message_to_component does not change between type: clear_pdf.
    # apparently, streamlit will not rerun the .html() if no changes were made.
    st.session_state.message_to_component = {"type": "CLEAR_PDF", "message_id": str(uuid.uuid4())}


def set_pdf_to_display(pdf_link, page_number=None):
    if pdf_link == st.session_state.pdf_to_display and page_number == st.session_state.pdf_page_number:
        print(f"PDF already set to {st.session_state.pdf_to_display} on page {st.session_state.pdf_page_number}, no need to update.")
        return
    # lambda: setattr(st.session_state, 'pdf_to_display', document_link)
    print(f"Changing pdf to display: {st.session_state.pdf_to_display}, to pdf {pdf_link}")
    # print(f"Setting pdf to display: {pdf_link} on page: {page_number}")
    # st.session_state.pdf_to_display = pdf_link
    # st.session_state.pdf_page_number = page_number
    st.session_state.message_to_component = {"type": 'POPOVER_CLICKED', "documentLink": pdf_link, "pageNumber": page_number}
    # print(f"Set pdf to display: {st.session_state.pdf_to_display}")

def displayPDF(file_name, page_number=None):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join("app", "static")
    ALLOWED_PDF_DIR = os.path.join(APP_ROOT, STATIC_DIR)

    real_file_path = os.path.join(ALLOWED_PDF_DIR, file_name)

    # print(f"Real file path: {real_file_path}")

    if not os.path.realpath(real_file_path).startswith(os.path.realpath(ALLOWED_PDF_DIR)):
        raise Exception("Path not allowed, only serves PDF from static folder ", ALLOWED_PDF_DIR)
    
    secure_file_path = os.path.join(STATIC_DIR, file_name)

    if not (isinstance(page_number, int) or page_number is None):
        print(f"Page number is not an integer: {page_number}, type: {type(page_number)}")
        raise Exception("Page number must be an integer")
    
    # print(f"[displayPDF] UNSECURE File name: {file_name}, page number: {page_number}")

    secure_page_number = str(page_number) if page_number is not None else ""

    # print("FILE_NAME: ", file_name)
    if file_name == "solvency-II-files\\guidelines-level 3-v0.1 - TRUNCATED\\Joint ESA Gls MiCAR %28JC 2024 28%29_EN.pdf":
        # naming issue, so renamed in static folder as well. temporary work around.
        print(f"File replaced: {real_file_path}")
        secure_file_path = os.path.join(STATIC_DIR, "solvency-II-files\\guidelines-level 3-v0.1 - TRUNCATED\\Joint ESA Gls MiCAR JC 2024_EN.pdf")


    # print("[displayPDF] Displaying pdf with: ", secure_file_path, " page number: ", secure_page_number)
    cache_bust = str(st.session_state.pdf_cache_bust) # NOT WORKING unless, edge://settings/privacy/sitePermissions/allPermissions/pdfDocuments --> PDF view settings

    pdf_display = f'<iframe id=pdf_sidebar src="{secure_file_path}?cache_bust={cache_bust}#page={secure_page_number}" width="600" height="550" style="width:100%;" type="application/pdf"></iframe>'
    
    if st.session_state.prev_pdf_for_cache_bust != file_name or st.session_state.prev_page_number != page_number:
        print(f"[displayPDF] Setting cache bust to {cache_bust} for file {file_name} (prev_pdf {st.session_state.prev_pdf_for_cache_bust})")
        st.session_state.pdf_cache_bust = str(uuid.uuid4())
        st.session_state.prev_pdf_for_cache_bust = file_name
        st.session_state.prev_page_number = page_number
    else:
        print(f"[displayPDF] caching the pdf")

    # Displaying File
    with st.container(key=f"pdf-display-container"):
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
    # st.session_state.message_to_component = None

# SETTING STATE FOR DISPLAY PDF THROUGH FOR BUTTONS IN POPOVER
with sidebar:
    result = my_component("Debugger for messenger", "messenger")
    print("messenger result: ", result)
    # print(f"Type of result: {type(result)}")
    document_link_through_link = None
    page_number_through_link = None
    if not result == 0:
        document_link_through_link = result["documentLink"]
        page_number_through_link = int(result["pageNumber"]) if isinstance(result["pageNumber"], str) else result["pageNumber"]
    # prev_document_link_through_link = st.session_state.get("document_link_through_link", None)
    # prev_page_number_through_link = st.session_state.get("pdf_page_number", None)
    # print(f"Document link through link: {document_link_through_link}, page number: {page_number_through_link}")

# print(f"Document link through link: {document_link_through_link}, prev: {prev_document_link_through_link}   ")
# if document_link_through_link != prev_document_link_through_link or page_number_through_link != prev_page_number_through_link:
#     # print(f"Changed Document Link: {document_link_through_link}, previous: {prev_document_link_through_link}")
#     # print(f"type of document link: {type(document_link_through_link)}, previous: {type(prev_document_link_through_link)}")
#     # update pdf to display if change is detected
#     # st.session_state.pdf_to_display = document_link_through_link
#     if st.session_state.document_link_through_link == "JUST_CLOSED":
#         print("JUST CLOSED")
#         st.session_state.document_link_through_link = st.session_state.pdf_to_display
#     else: 
#         set_pdf_to_display(document_link_through_link, page_number=page_number_through_link) 
#     st.session_state["document_link_through_link"] = document_link_through_link

st.session_state.pdf_to_display = document_link_through_link
st.session_state.pdf_page_number = page_number_through_link

print(f"Loaded document link link: {document_link_through_link}")

# DISPLAY SOURCES FUNCTION
def displaySources(link):
    added_sources = []
    document_sources_grouped_by_link = {}
    for document_source in link:
        if document_source["link"] not in added_sources:
            # check if title is not set in metadata
            # print(f"Title: used {title}")
            
            added_sources.append(document_source["link"])
            document_sources_grouped_by_link[document_source["link"]] = [document_source]
        else: 
            document_sources_grouped_by_link[document_source["link"]].append(document_source)
    
    # query_id should be the same for all sources.
    query_id = link[0]["query_id"]
    container_key = f"sources-buttons-container-{query_id}".replace(" ", "-")

    # TO CHANGE. Include in global styling with container_key start with sources-container-
    st.markdown(
        f"""
        <style>
            .st-key-{container_key} {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 2fr));
                gap: 1rem;

                > * {{
                        flex: 1;
                        display: flex

                        & > * {{
                            flex: 1;
                        }}
                }}
            }}

            .st-key-{container_key} > * {{
                    display: flex
            }}

            .st-key-{container_key} > * > * {{
                    flex: 1;
                    display: flex            
            }}

            .st-key-{container_key} > * > * > * {{
                    flex: 1;     
            }}

            .st-key-{container_key} button > span {{
                margin-right: 0.5rem;
                justify-content: flex-start;
                flex-shrink: 0;
            }}

            .st-key-{container_key} button > div {{
                flex-grow: 1;
            }}

            [class*="st-key-source-block-container-"] {{
                gap: 0rem;
            }}
        </style>
        """, unsafe_allow_html=True
    )
    
    # with st.container(border=True):
    # with st.container(key=container_key):
    for link in document_sources_grouped_by_link:
        with st.container(border=True):
            st.markdown("#### Document: " + document_sources_grouped_by_link[link][0]["short_title"])
            for document_source in document_sources_grouped_by_link[link]:
                document_link = document_source["link"]
                page_number = document_source.get("page_number", None)

                PAGE_CONTENT_LENGTH_LIMIT = 250

                truncated_page_content = document_source["page_content"] #if len(document_source["page_content"]) <= PAGE_CONTENT_LENGTH_LIMIT else document_source["page_content"][:PAGE_CONTENT_LENGTH_LIMIT] + "..."

                non_empty_headings = [re.sub(r"\*{1,2}", r"", heading) for heading in document_source["heading_hierarchy"] if heading != ""]
                last_heading = non_empty_headings[-1] if non_empty_headings else "Part of " + document_source["short_title"]
                print(f"non empty headings: {non_empty_headings}")


                print(f"[DisplaySources] Document link: {document_source["link"]}, page number: {page_number}")
                with st.container(key=f"source-block-container-{document_source['id']}"):
                    st.button(
                        key=f"{document_source["id"]}",
                        label=f"Source {document_source["source_index"]}: {last_heading}", 
                        on_click= set_pdf_to_display, 
                        args=(document_link, page_number), #args in python need to give not wrapped with function as in js
                        icon="🔗"
                    )

                    st.html(f"<blockquote>{md.render(truncated_page_content)}</blockquote>")


 # LAYOUT OF MAIN PAGE
chat_col, pdf_col = st.columns([1, 1])

with chat_col:
    chat_col.title("💬 Regulation Search")
    chat_col.caption("🚀 Powered by Triple A")

    # with st.popover("test"):
    #     st.markdown("# Test")

# with pdf_col:
#     st.markdown('<iframe id=pdf_sidebar_test src="http://localhost:8501/app/static/solvency-II-files/guidelines-level%203-v0.1%20-%20TRUNCATED/Guidelines%20on%20Own%20Risk%20Solvency%20Assessment%20.pdf#page=4" width="600" height="550" type="application/pdf"></iframe>', unsafe_allow_html=True)

    
# PDF INTERFACE
if st.session_state.pdf_to_display:
    # WARNING : pdf_to_display through buttons in displaySources OR by clicking on buttons in the popovers.
    print("pdf: ", st.session_state.pdf_to_display)
    with pdf_col:
        displayPDF(st.session_state.pdf_to_display, st.session_state.pdf_page_number)    

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
            const pageNumber = button.dataset.pageNumber || null;
            console.log(documentLink);
            console.log("pageNumber: ", pageNumber);
            // button.style.color = "red";
            componentWindow.postMessage({
                type: 'POPOVER_CLICKED',
                documentLink: documentLink,
                pageNumber: pageNumber,  // Use dataset to get page number if available
            }, '*'); // In production, use the component's actual origin instead of '*'

        }
        popover_elements.forEach(element => {element.addEventListener("click", (e) => {handlePopoverClick(e)})})
    }
</script>
"""

def escape_curly_braces(text: str) -> str:
    return text.replace("{", "{{").replace("}", "}}")

footer = st.container(key="footer-container") # dump for any container with no visual elements

# CHAT INTERFACE
with chat_col:
    messages_container = chat_col.container()
    messages_container.chat_message("assistant").write("Hello, I am here to help search through documents related to Solvency II")

    token_count = 0
    for message in st.session_state.messages:
            if message["role"] == "system":
                continue

            if message["role"] == "user":
                with messages_container.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if message["role"] == "assistant":
                chat_tab, sources_tab = messages_container.tabs(["Chat", "Sources"])
                print(f"Message: {message}")
                with chat_tab:
                    if "thoughts" in message and message["thoughts"] != "":
                        with st.chat_message("assistant", avatar="💭"):
                            thought_expander = st.expander("**Thoughts...**")
                            thought_expander.write(message["thoughts"])         

                    with footer:
                        # hide styling and script from main container.
                        components.html(popover_elements_event_listener, height=0, width=0) 

                    if "popover_elements" in message and message["popover_elements"] != "":
                            # load in event listeners for popover buttons
                            footer.html(message["popover_elements"])

                    with st.chat_message(message["role"]):
                        st.markdown(message["content"], unsafe_allow_html=True)

                if "rate_limit_error" in message and message["rate_limit_error"] != None:
                    messages_container.error("Rate limit exceeded, please try again later.")
                    print("Rate limit exceeded, please try again later.")
        
                if "relevance_scores" in message and message["relevance_scores"] != []:
                    avg = sum(message["relevance_scores"]) / len(message["relevance_scores"])
                    MAGIC_LOW = 0.2
                    MAGIC_HIGH = 0.8
                    if avg < MAGIC_LOW:
                        messages_container.warning(f"It looks like there aren’t many great matches for your search. Try using words that might appear in the article you’re looking for.")
                        if debug_mode:
                            messages_container.warning(f"Average relevance score of documents is low (0 <= score < 0.2): {avg:.2f}. Consider changing the question and writing out abbreviations")
                    elif avg > MAGIC_HIGH:
                        messages_container.success(f"It looks like there are some great matches for your search.")
                        if debug_mode:
                            messages_container.success(f"Average relevance score of documents is high (0.8 < score <= 1): {avg:.2f}.")

                with sources_tab:
                    # sources_tab.subheader("Sources tab")
                    if "sources" in message:
                        with sources_tab: # .chat_message("assistant", avatar="🔗")
                            # print("message sources: ")
                            # pprint.pprint(message["sources"])
                            displaySources(message["sources"])

            # add token count
            if "token_count" in message:
                token_count += message["token_count"]
        
    sidebar.markdown(f"Total token count: {round(token_count)}")

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
        
        chunks_concatenated = ""
        document_sources = []
        query_id = str(uuid.uuid4())
        # if embedding_model_option.value["data-ingestion-pipeline"] == "v1":
        #     raise Exception("No longer supported, use v2 data ingestion pipeline (reason reranker).")
        
        #     for idx, document in enumerate(matched_documents):
        #         source = f"{document.metadata["source"]} on page {document.metadata["page_label"]}"
        #         #note: unsure why metadata has a page and page_label attribute?, verified that page_label was correct for data kwality pdf
        #         document_sources.append(source)
        #         chunks_concatenated += f"###\n source {idx}, ref {source}:\n\n {document.page_content} \n\n\n"
        
        matched_documents = None
        relevance_scores = []
        if reranker_model is None:
            matched_documents = vectorstore.similarity_search(query=query,k=k)
            # matched_documents = reranker_model.rerank(query=query, documents=matched_documents)
        else:
            print(f"[INFO] Reranking documents with {reranker_model_option.value['model']}")
            
            # create retriever + reranker
            compressor = ContextualCompressionRetriever(base_compressor=reranker_model, 
                                        base_retriever=retriever
            )

            reranked_documents = compressor.invoke(query)

            matched_documents = reranked_documents
            relevance_scores = [doc.metadata["relevance_score"] for doc in matched_documents]

            print(f"Relevance scores: {relevance_scores}")
            st.session_state.relevance_scores = relevance_scores

        for idx, chunk in enumerate(matched_documents):

            source_index = idx + 1

            # define metadata
            title = ""
            if "title" in chunk.metadata and chunk.metadata["title"] != "":
                title = chunk.metadata["title"]
            else: 
                title = str(chunk.metadata["source"]).split("data\\raw\\solvency-II-files\\")[-1]
                title = title.replace("guidelines-level 3-v0.1 - TRUNCATED\\", "guidelines-level-3: ")

            # short title is used for display in the UI, so it is shorter than the full title
            if not "short_title" in chunk.metadata:
                short_title = get_short_title(chunk.metadata["source"].split("\\")[-1])
            else:
                short_title = chunk.metadata["short_title"]

            header_1 = chunk.metadata.get("Header 1", "")
            header_2 = chunk.metadata.get("Header 2", "")
            header_3 = chunk.metadata.get("Header 3", "")
            if embedding_model_option.value["data-ingestion-pipeline"] == "v3":
                header_4 = chunk.metadata.get("Header 4", "")
                header_5 = chunk.metadata.get("Header 5", "")
            else:
                header_4 = ""
                header_5 = ""

            heading_hierarchy = [header_1, header_2, header_3, header_4, header_5]

            # print(f"\n* keywords: {chunk.metadata["keywords"]}\n" if "keywords" in chunk.metadata  and chunk.metadata["keywords"] != "" else "")

            source_metadata = ""
            source_metadata += f"* Title: {title}"
            source_metadata += f"\n* keywords: {chunk.metadata["keywords"]}\n" if "keywords" in chunk.metadata  and chunk.metadata["keywords"] != "" else ""
            source_metadata += f"\n* Author: {chunk.metadata["Author"]}\n" if "Author" in chunk.metadata else ""
            source_metadata += f"\n* Header 1: {header_1}\n" if header_1 else ""
            source_metadata += f"\n* Header 2: {header_2}\n" if header_2 else ""
            source_metadata += f"\n* Header 3: {header_3}\n" if header_3 else ""

            if embedding_model_option.value["data-ingestion-pipeline"] == "v3":
                # additional metadata is available
                # namely: page_number, short_title
                # in addition: improved structure extraction:
                # now for solvency level 1 and level 2 you have 5 heading levels instead of 3 (and improved quality), TITLE, CHAPTER, Section, Subsection, Article
                source_metadata += f"\n* Header 4: {header_4}\n" if header_4 else ""
                source_metadata += f"\n* Header 5: {header_5}\n" if header_5 else ""

            # document_source is the UI data format, used to both display pdf sources, and page_content on click
            document_source = {
                    "id": str(uuid.uuid4()),
                    "source_index": source_index,
                    "link": str(chunk.metadata["source"]).split("data\\raw\\")[-1],
                    "title": title,
                    "short_title": short_title,
                    "page_content": chunk.page_content,
                    "query": query,
                    "query_id": query_id
                }

            if embedding_model_option.value["data-ingestion-pipeline"] == "v3" or embedding_model_option.value["data-ingestion-pipeline"] == "v4":
                # add additional metadata for v3 data ingestion pipeline
                document_source["page_number"] = chunk.metadata.get("page_number", "")
                document_source["heading_hierarchy"] = heading_hierarchy
 

            document_sources.append(document_source)

            chunks_concatenated += f"\n ### source {source_index} \n\n metadata:\n {source_metadata}:\n\n extract:\n\n {chunk.page_content} \n\n\n"

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

        st.session_state.messages.append({"role": "user", "content": query, "prompt": prompt, "token_count": count_tokens(prompt)})
        
        # change to add the context of previous parts.

        chat = [("system", generation_instructions) , ]

        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            if message["role"] == "user":
                escaped_prompt = escape_curly_braces(message["prompt"])
                chat.append(("user", escaped_prompt))
            elif message["role"] == "assistant":
                # text may contain latex with curly braces: \\text{Operational Risk}
                escaped_content_unformatted = escape_curly_braces(message["content_unformatted"])
                chat.append(("assistant", escaped_content_unformatted))

        chat.append(("user", prompt))

        # Note: potential problem with sources ids overlapping of different chat (e.g. source 1, from previous prompt, with current source 1 from current prompt), may confuses the LLM?
        # print("Chat history for LLM:")
        # pprint.pprint(chat)

        count_tokens(prompt)

        chat_template = ChatPromptTemplate(chat)
        
        formatted_chat_message = chat_template.format_messages()
        
        # print(f"PROMPT FOR LLM: \n\n")
        # pprint.pprint(formatted_chat_message)      
        # print("\n\n END OF PROMPT OUTPUT \n")

        if debug_mode:
            from langchain.schema import SystemMessage, HumanMessage
            messages_as_dict = [
                {
                    "role": "system" if isinstance(m, SystemMessage) else "human",
                    "content": m.content
                }
                for m in formatted_chat_message
            ]
            with open("prompt.json", "w", encoding="utf-8") as f:
                json.dump(messages_as_dict, f, indent=4, ensure_ascii=False)
        
        rate_limit_error = None

        try:
            response_stream = llm.stream(formatted_chat_message)

            # print(f"Response stream ended with entire response: {response_stream}")
            
            last_human_prompt = formatted_chat_message[-1].content
            
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
                            if ai_message["type"] == "thinking":
                                # extract bold part of the text
                                thought = ai_message["thinking"]
                                thought_topic = thought.splitlines()[0]
                                # stream_thinking_container.info(thought_topic)
                                thought_expander = stream_thinking_container.expander(thought_topic)
                                response_thinking += thought
                                thought_expander.write(response_thinking)
                                last_thought_topic = thought_topic
                            else:
                                raise Exception("[UNKNOWN STATE] Not sure which ai_messages are listed content here.")
                    else:
                        raise Exception("[UNKNOWN STATE] Not implemented AIMessageChunk content can only be a list or str.")                
                else:
                    raise Exception("[UNKNOWN STATE] The chunk can only be a string or a thinking chunk.")
        except OpenAIRateLimitError as e:
            messages_container.error("Rate limit exceeded, please try again later.")
            rate_limit_error = e
            print("Rate limit exceeded, please try again later.")
            # response_without_thinking = "Rate limit exceeded, please try again later."
            # if debug_mode:
            #     raise e
        # st.session_state.expanded_thoughts = expanded_thoughts

        def convert_sources_to_interactive(text, document_sources):
            def findPage(document_sources, source_num):
                # debug_last_index = -1
                for document_source in document_sources:
                    # debug_last_index = document_source["source_index"]
                    # print(f"Debug index: {debug_last_index}")
                    # print(f"Source_num ... :{source_num}")
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
                source_numbers = [num.strip() for num in source_numbers_group.split(',')]

                for source_num in source_numbers:
                    if source_num == "":
                        continue
                    elif isinstance(source_num, str) and not source_num.isdigit():
                        print(f"Source was not an int: {source_num}, type: {type(source_num)}")
                        continue

                    document_source = findPage(document_sources, source_num)
                    
                    page_content = document_source["page_content"]
                    document_link = document_source["link"]
                    page_number = document_source.get("page_number", None)
                    heading_hierarchy = document_source["heading_hierarchy"]
                    # remove italic or bold markdown from headings
                    print(f"Heading hierarchy: {heading_hierarchy}")
                    html_non_empty_headings = [re.sub(r"\*{1,2}", r"", heading) for heading in heading_hierarchy if heading != ""]
                    print(f"HTML non-empty headings: {html_non_empty_headings}")
                    query_id = document_source["query_id"]

                    # due to streamlit filtering out inline js when invoking container.html(), e.g. onclick listeners. The onclick listeners are attached seperately in an iframe component
                    button_view_pdf =  f"""
                        <button id="pop-button-{document_source["id"]}-{source_num}" data-document-link="{document_link}" data-page-number="{page_number}" style="
    display: block;
    font-weight: 400;
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    min-height: 2.5rem;
    margin: 0px;
    line-height: 1.6;
    user-select: none;
    background-color: rgb(255, 255, 255);
    border: 1px solid rgba(49, 51, 63, 0.2);
">View PDF of {document_source["short_title"]}</button>
    """

                    # pprint.pprint(page_content_with_button)
                    # st-cf st-cg st-ch
                    # streamlit_popover_styling_classes = "st-bb st-es st-et st-eu st-ev st-ew st-ex st-fh st-b5 st-fi st-f0 st-f1 st-f2 st-f3 st-f4 st-f5 st-f6 st-f7 st-av st-aw st-ax st-ay st-f8 st-f9 st-fa st-fb st-az st-b0 st-b1 st-b2 st-fc st-fd st-fe st-ff"
                    streamlit_popover_styling_classes = ""

                    # need to convert markdown without triggering streamlit render, under the hood streamlit uses markdown-it-py
                    html_page_content = md.render(page_content)
                    popover_elements += f"""
                    <style>
                    [popovertarget="pop-{document_source["id"]}-{source_num}"]{{
                        anchor-name: --pop-{document_source["id"]}-{source_num};
                    }}

                    #pop-{document_source["id"]}-{source_num} {{
                        position-anchor: --pop-{document_source["id"]}-{source_num};
                        position-area: bottom;
                        max-width: 40%;
                        margin: 0;
                        overflow-y: scroll;
                        position-try-fallbacks: flip-block, flip-inline, flip-start;
                        position-try: flip-block, flip-inline, flip-start;
                    }}
                    blockquote {{
                        background-color: #f0f9ff;  
                        border-left: 5px solid #007bff;  
                        padding: 20px;  
                        margin: 20px 0;  
                        font-style: italic;  
                        color: #333;  
                        border-radius: 5px;  
                        position: relative;  
                    }}
            
                    blockquote::before {{  
                        content: "“";  
                        font-size: 4em;  
                        color: rgba(0, 123, 255, 0.2);  
                        position: absolute;  
                        top: -10px;  
                        left: 10px;  
                    }}  

                    blockquote cite {{ 
                        display: block;  
                        margin-top: 10px;  
                        font-size: 0.9em;  
                        color: #555;  
                    }}  
                    </style>             
                    <div popover id="pop-{document_source["id"]}-{source_num}" class="{streamlit_popover_styling_classes}">
                        <h3>{document_source["short_title"]}</h3>
                        <h4>{" > ".join(html_non_empty_headings)}</h4>
                        <blockquote>
                            <p>{html_page_content}</p>
                        </blockquote>
                        {button_view_pdf}
                    </div>
                    """

                    # print("Page_content: ")
                    # print(type(page_content))
                    # pprint.pprint(page_content)

                    popover_target += f"""<span><button popovertarget="pop-{document_source["id"]}-{source_num}">Source {source_num}</button></span>"""

                return popover_target

            pattern = r"(Source|Bron|Sources)\s((\d+,?\s?)+)"
            

            return re.sub(pattern, replacer, text), popover_elements
                    
        # print(f"Response without thinking: {response_without_thinking}")
        sourced_response, popover_elements = convert_sources_to_interactive(response_without_thinking, document_sources)

        # print("Popover elements: ", popover_elements)

        st.session_state.messages.append({
            "role": "assistant", 
            "sources": document_sources, 
            "content": sourced_response, 
            "content_unformatted": response_without_thinking, 
            "popover_elements": popover_elements, 
            "thoughts": response_thinking, 
            "relevance_scores": relevance_scores,
            "rate_limit_error": rate_limit_error,
            "token_count": count_tokens(response_without_thinking)
        })

        # force a rerun to update the sources.
        if not debug_mode:
            st.rerun()


