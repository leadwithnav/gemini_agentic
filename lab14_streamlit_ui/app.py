import os
import uuid

import httpx
import streamlit as st

from google.auth.transport.requests import Request
from google.oauth2.id_token import fetch_id_token


# ============================================================
# Configuration
# ============================================================

ADK_BASE_URL = os.getenv(
    "ADK_BASE_URL",
    "http://localhost:8081",
)

APP_NAME = os.getenv(
    "APP_NAME",
    "lab9_cloud_run.app.configured_agent",
)

USER_ID = os.getenv(
    "USER_ID",
    "demo-user",
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="CME Support Console",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .sub-title {
        color: #6b7280;
        font-size: 16px;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        padding: 18px;
        border-radius: 12px;
        background: white;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
    }

    .result-box {
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Authentication
# ============================================================

def get_auth_headers():
    """
    Local:
        Cloud Run proxy handles authentication.

    Cloud Run:
        Streamlit service obtains an ID token using its
        service account and calls the private ADK service.
    """

    if (
        ADK_BASE_URL.startswith("http://localhost")
        or ADK_BASE_URL.startswith("http://127.0.0.1")
    ):
        return {}

    token = fetch_id_token(
        Request(),
        ADK_BASE_URL,
    )

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# ADK API
# ============================================================

def create_session(session_id: str):

    url = (
        f"{ADK_BASE_URL}/apps/{APP_NAME}"
        f"/users/{USER_ID}/sessions/{session_id}"
    )

    response = httpx.post(
        url,
        json={},
        headers=get_auth_headers(),
        timeout=30.0,
    )

    response.raise_for_status()

    return response.json()


def run_agent(
    session_id: str,
    message: str,
):

    url = f"{ADK_BASE_URL}/run"

    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": message
                }
            ],
        },
    }

    response = httpx.post(
        url,
        json=payload,
        headers=get_auth_headers(),
        timeout=120.0,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Extract Agent Response
# ============================================================

def extract_answer(events):

    if not isinstance(events, list):
        return str(events)

    for event in reversed(events):

        content = event.get("content")

        if not content:
            continue

        parts = content.get("parts", [])

        texts = [
            part["text"]
            for part in parts
            if isinstance(part, dict)
            and part.get("text")
        ]

        if texts:
            return "\n".join(texts)

    return "Agent completed the request but returned no text response."


# ============================================================
# Helper
# ============================================================

def ask_agent(prompt: str):

    try:

        with st.spinner("CME Agent is processing..."):

            events = run_agent(
                st.session_state.session_id,
                prompt,
            )

            return extract_answer(events)

    except httpx.HTTPStatusError as e:

        return (
            f"### Request Failed\n\n"
            f"Status: `{e.response.status_code}`\n\n"
            f"```text\n{e.response.text}\n```"
        )

    except Exception as e:

        return (
            "### Error calling CME Agent\n\n"
            f"`{e}`"
        )


# ============================================================
# Session Initialization
# ============================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(uuid.uuid4())

    try:

        create_session(
            st.session_state.session_id
        )

        st.session_state.connected = True
        st.session_state.connection_error = None

    except Exception as e:

        st.session_state.connected = False
        st.session_state.connection_error = str(e)


if "chat_messages" not in st.session_state:

    st.session_state.chat_messages = []


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.title("CME Support")

    st.caption(
        "AI-powered internal support console"
    )

    st.divider()

    if st.session_state.connected:

        st.success("● Agent Connected")

    else:

        st.error("● Agent Disconnected")

        if st.session_state.connection_error:
            st.caption(
                st.session_state.connection_error
            )

    st.write("### Environment")

    if ADK_BASE_URL.startswith("http://localhost"):
        st.code("Local → Cloud Run Proxy")
    else:
        st.code("Google Cloud Run")

    st.write("### Application")

    st.code(APP_NAME)

    st.write("### Session")

    st.caption(
        st.session_state.session_id[:18] + "..."
    )

    st.divider()

    st.write("### Support Domains")

    st.write("📦 Product Support")
    st.write("📈 Market Status")
    st.write("🚨 Incident Support")
    st.write("🩺 Product Health")

    st.divider()

    if st.button(
        "🔄 Start New Session",
        use_container_width=True,
    ):

        try:

            new_session_id = str(uuid.uuid4())

            create_session(
                new_session_id
            )

            st.session_state.session_id = new_session_id
            st.session_state.chat_messages = []
            st.session_state.connected = True
            st.session_state.connection_error = None

            st.rerun()

        except Exception as e:

            st.error(
                f"Unable to create session: {e}"
            )


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="main-title">
        CME Support Console
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
        AI-assisted product, market and incident support
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Status Metrics
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Agent",
        "Online"
        if st.session_state.connected
        else "Offline",
    )

with col2:

    st.metric(
        "Supported Products",
        "4",
        help="NQ, ES, CL and GC",
    )

with col3:

    st.metric(
        "Support Domains",
        "3",
        help="Product, Market Status and Incident Support",
    )

with col4:

    st.metric(
        "Backend",
        "ADK",
    )


st.divider()


# ============================================================
# Main Tabs
# ============================================================

tabs = st.tabs(
    [
        "🏠 Dashboard",
        "📦 Product Lookup",
        "📈 Market Status",
        "🚨 Incidents",
        "🩺 Health Check",
        "💬 Ask Agent",
    ]
)


# ============================================================
# Dashboard
# ============================================================

with tabs[0]:

    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    with col1:

        with st.container(border=True):

            st.markdown("### 📦 Product Support")

            st.write(
                "Retrieve product specifications, "
                "contract size, tick size and asset class."
            )

            if st.button(
                "Get NQ Details",
                use_container_width=True,
            ):

                result = ask_agent(
                    "What are the complete product details for NQ?"
                )

                st.markdown(result)

    # --------------------------------------------------------
    # Market
    # --------------------------------------------------------

    with col2:

        with st.container(border=True):

            st.markdown("### 📈 Market Status")

            st.write(
                "Check whether a CME product "
                "is currently trading."
            )

            if st.button(
                "Check NQ Market",
                use_container_width=True,
            ):

                result = ask_agent(
                    "Is NQ currently trading?"
                )

                st.markdown(result)

    # --------------------------------------------------------
    # Incident
    # --------------------------------------------------------

    with col3:

        with st.container(border=True):

            st.markdown("### 🚨 Incident Support")

            st.write(
                "Find operational incidents "
                "affecting CME products."
            )

            if st.button(
                "Check NQ Incidents",
                use_container_width=True,
            ):

                result = ask_agent(
                    "Show all incidents affecting NQ."
                )

                st.markdown(result)

    st.divider()

    st.subheader("How Requests Are Routed")

    st.code(
        """
User Request
     │
     ▼
CME ADK Router Agent
     │
 ┌───┴───────────────┐
 │                   │
 ▼                   ▼
Product / Market    Incident
Support             Support
 │                   │
 ▼                   ▼
BigQuery             MCP
                      │
                      ▼
                   REST API
        """,
        language="text",
    )


# ============================================================
# Product Lookup
# ============================================================

with tabs[1]:

    st.subheader("📦 Product Lookup")

    st.caption(
        "Retrieve product specifications using the CME Product Support Agent."
    )

    col1, col2 = st.columns(2)

    with col1:

        symbol = st.selectbox(
            "Product Symbol",
            [
                "NQ",
                "ES",
                "CL",
                "GC",
            ],
            key="product_symbol",
        )

    with col2:

        product_detail = st.selectbox(
            "Information Required",
            [
                "Complete product details",
                "Contract size",
                "Tick size",
                "Asset class",
                "Product description",
            ],
        )

    if st.button(
        "🔍 Retrieve Product Information",
        type="primary",
        use_container_width=True,
    ):

        prompt = (
            f"For CME product {symbol}, "
            f"provide {product_detail.lower()}."
        )

        result = ask_agent(prompt)

        st.subheader("Result")

        with st.container(border=True):
            st.markdown(result)


# ============================================================
# Market Status
# ============================================================

with tabs[2]:

    st.subheader("📈 Market Status")

    st.caption(
        "Check current trading status for CME products."
    )

    products = st.multiselect(
        "Select Products",
        [
            "NQ",
            "ES",
            "CL",
            "GC",
        ],
        default=["NQ"],
    )

    if st.button(
        "Check Market Status",
        type="primary",
        use_container_width=True,
    ):

        if not products:

            st.warning(
                "Select at least one product."
            )

        else:

            columns = st.columns(
                min(len(products), 4)
            )

            for index, product in enumerate(products):

                with columns[
                    index % len(columns)
                ]:

                    with st.container(border=True):

                        st.markdown(
                            f"### {product}"
                        )

                        result = ask_agent(
                            f"Is {product} currently trading? "
                            f"Provide its current market status."
                        )

                        st.markdown(result)


# ============================================================
# Incident Explorer
# ============================================================

with tabs[3]:

    st.subheader("🚨 Incident Explorer")

    st.caption(
        "Retrieve incidents using the Incident Support Agent and MCP server."
    )

    search_type = st.radio(
        "Search By",
        [
            "Product Symbol",
            "Incident ID",
        ],
        horizontal=True,
    )

    # --------------------------------------------------------
    # Search by Product
    # --------------------------------------------------------

    if search_type == "Product Symbol":

        incident_symbol = st.selectbox(
            "Product",
            [
                "NQ",
                "ES",
                "CL",
                "GC",
            ],
            key="incident_symbol",
        )

        if st.button(
            "Find Incidents",
            type="primary",
            use_container_width=True,
        ):

            result = ask_agent(
                f"Show all incidents affecting "
                f"{incident_symbol}."
            )

            st.subheader(
                f"Incidents for {incident_symbol}"
            )

            with st.container(border=True):
                st.markdown(result)

    # --------------------------------------------------------
    # Search by Incident ID
    # --------------------------------------------------------

    else:

        incident_id = st.text_input(
            "Incident ID",
            placeholder="Example: INC-101",
        )

        if st.button(
            "Get Incident Details",
            type="primary",
            use_container_width=True,
        ):

            if not incident_id:

                st.warning(
                    "Enter an incident ID."
                )

            else:

                result = ask_agent(
                    f"Show complete details for "
                    f"incident {incident_id}."
                )

                st.subheader(
                    "Incident Details"
                )

                with st.container(border=True):
                    st.markdown(result)


# ============================================================
# Product Health Check
# ============================================================

with tabs[4]:

    st.subheader("🩺 Product Health Check")

    st.caption(
        "Run an end-to-end support check across multiple capabilities."
    )

    st.info(
        """
        This workflow combines:

        **Product Information → Market Status → Incident Status**
        """
    )

    health_product = st.selectbox(
        "Select Product",
        [
            "NQ",
            "ES",
            "CL",
            "GC",
        ],
        key="health_product",
    )

    if st.button(
        "🩺 Run Comprehensive Health Check",
        type="primary",
        use_container_width=True,
    ):

        result = ask_agent(
            f"Perform a comprehensive product health check "
            f"for {health_product}. "
            f"Include product details, current market status "
            f"and active incidents."
        )

        st.success(
            f"Health check completed for {health_product}"
        )

        with st.container(border=True):
            st.markdown(result)


# ============================================================
# Ask Agent
# ============================================================

with tabs[5]:

    st.subheader("💬 Ask CME Support Agent")

    st.caption(
        "Use natural language for questions outside the structured workflows."
    )

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Ask a CME support question..."
    )

    if prompt:

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):

            st.markdown(prompt)

        with st.chat_message("assistant"):

            result = ask_agent(prompt)

            st.markdown(result)

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": result,
            }
        )