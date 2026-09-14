"""
Lab 4 Student Challenge:
BigQuery Tool Initialization

Goal:
Configure Google ADK's built-in BigQueryToolset so that the Exchange Information Assistant can query:
- cme_support.exchanges
- cme_support.exchange_products

Students must complete:
1. Project ID & Dataset ID state resolution.
2. BigQuery credentials configuration.
3. Read-only tool configuration (WriteMode.BLOCKED).
4. BigQueryToolset creation & tool filtering.
"""

import os
from pathlib import Path
import google.auth
from dotenv import load_dotenv

from google.adk.tools.bigquery import (
    BigQueryCredentialsConfig,
    BigQueryToolset,
)
from google.adk.tools.bigquery.config import (
    BigQueryToolConfig,
    WriteMode,
)


# ============================================================
# 1. LOAD ENVIRONMENT
# ============================================================

PARENT_ENV = Path(__file__).resolve().parent.parent / ".env"

if PARENT_ENV.exists():
    load_dotenv(dotenv_path=PARENT_ENV)
else:
    load_dotenv()


# ============================================================
# 2. CONFIGURATION
# ============================================================

MODEL = "gemini-2.5-flash"
DATASET_ID = "cme_support"


# ============================================================
# 3. GOOGLE CLOUD AUTHENTICATION
# ============================================================

application_default_credentials, detected_project_id = google.auth.default()


# ============================================================
# 4. RESOLVE & VALIDATE PROJECT
# ============================================================

PROJECT_ID = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("GCLOUD_PROJECT")
    or detected_project_id
)

if not PROJECT_ID:
    raise RuntimeError(
        "Unable to determine Google Cloud project ID.\n"
        "Set GOOGLE_CLOUD_PROJECT or configure ADC correctly.\n\n"
        "Example:\n"
        "gcloud config set project <PROJECT_ID>\n"
        "gcloud auth application-default login"
    )


# ============================================================
# 5. BIGQUERY CREDENTIALS (STUDENT TASK 2)
# ============================================================

# TODO 2: Create BigQueryCredentialsConfig using application_default_credentials
# credentials_config = BigQueryCredentialsConfig(....)
credentials_config = None  # TODO: Replace with BigQueryCredentialsConfig(....)


# ============================================================
# 6. READ-ONLY BIGQUERY CONFIGURATION (STUDENT TASK 3)
# ============================================================

# TODO 3: Configure BigQuery so write operations are blocked
# tool_config = BigQueryToolConfig(....)
tool_config = None  # TODO: Replace with BigQueryToolConfig(....)


# ============================================================
# 7. CREATE BIGQUERY TOOLSET (STUDENT TASK 4)
# ============================================================

# TODO 4: Create BigQueryToolset with credentials_config, bigquery_tool_config, and tool_filter
# bigquery_toolset = BigQueryToolset(....)
bigquery_toolset = None  # TODO: Replace with BigQueryToolset(....)