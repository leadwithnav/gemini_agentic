"""
BigQuery Tools Initialization & Authentication for ADK Agents (Lab 6).

Loads environment configuration from the workspace .env file,
provides Google Cloud Authentication, Project detection, and the read-only
BigQueryToolset instance.
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

# Load workspace .env file
PARENT_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
if PARENT_ENV.exists():
    load_dotenv(dotenv_path=PARENT_ENV)
else:
    load_dotenv()

# Configuration Constants
DATASET_ID = "cme_support"

# Google Cloud Authentication & Project Resolution
application_default_credentials, detected_project_id = google.auth.default()

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

# ADK Built-In BigQuery Toolset Setup (Read-Only)
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED
)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config,
    bigquery_tool_config=tool_config,
    tool_filter=[
        "get_table_info",
        "execute_sql",
    ],
)
