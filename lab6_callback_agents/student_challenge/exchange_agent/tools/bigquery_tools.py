"""
BigQuery Tools Initialization & Authentication

Used by the Product Information Agent.

Responsibilities:
- Load Google Cloud configuration
- Resolve Project ID
- Configure ADC credentials
- Create read-only BigQueryToolset
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
# 1. LOAD ENVIRONMENT CONFIGURATION
# ============================================================

PARENT_ENV = (
    Path(__file__).resolve().parent.parent / ".env"
)

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

application_default_credentials, detected_project_id = (
    google.auth.default()
)


# ============================================================
# 4. RESOLVE PROJECT ID
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
# 5. BIGQUERY CREDENTIAL CONFIG
# ============================================================

credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)


# ============================================================
# 6. READ-ONLY BIGQUERY CONFIGURATION
# ============================================================

tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED
)


# ============================================================
# 7. CREATE BIGQUERY TOOLSET
# ============================================================

bigquery_toolset = BigQueryToolset(

    credentials_config=credentials_config,

    bigquery_tool_config=tool_config,

    tool_filter=[
        "get_table_info",
        "execute_sql",
    ],
)