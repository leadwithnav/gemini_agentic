#!/usr/bin/env bash

# ==============================================================================
# Lab 4 Student Challenge
# CME Exchange Information Assistant - BigQuery Setup
#
# Creates:
#
#   cme_support.exchanges
#   cme_support.exchange_products
#
# The data replaces the local Python dictionaries/tools used
# in previous labs.
#
# The script is idempotent:
# it can be executed multiple times safely.
# ==============================================================================

set -e


# ==============================================================================
# STEP 1: RESOLVE PROJECT ID
# ==============================================================================

echo ""
echo "============================================================"
echo "Step 1: Validating Google Cloud Project"
echo "============================================================"


if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then

    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || true)

fi


if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then

    echo ""
    echo "ERROR: PROJECT_ID could not be determined."
    echo ""
    echo "Run one of:"
    echo ""
    echo "export PROJECT_ID=YOUR_PROJECT_ID"
    echo ""
    echo "or"
    echo ""
    echo "gcloud config set project YOUR_PROJECT_ID"
    echo ""

    exit 1

fi


echo ""
echo "Using Project:"
echo "$PROJECT_ID"


# ==============================================================================
# STEP 2: CREATE DATASET
# ==============================================================================

echo ""
echo "============================================================"
echo "Step 2: Creating BigQuery Dataset"
echo "============================================================"


if ! bq show \
    --project_id="$PROJECT_ID" \
    cme_support \
    &>/dev/null
then

    echo ""
    echo "Creating dataset: cme_support"

    bq mk \
        --dataset \
        --location=US \
        --description="Simulated CME support data for Agentic AI training" \
        --project_id="$PROJECT_ID" \
        cme_support

else

    echo ""
    echo "Dataset cme_support already exists."

fi


# ==============================================================================
# STEP 3: CREATE EXCHANGES TABLE
# ==============================================================================

echo ""
echo "============================================================"
echo "Step 3: Creating cme_support.exchanges"
echo "============================================================"


bq query \
    --nouse_legacy_sql \
    --project_id="$PROJECT_ID" \
    "
    CREATE TABLE IF NOT EXISTS
    \`${PROJECT_ID}.cme_support.exchanges\`
    (
        exchange_code STRING,
        exchange_name STRING,
        location STRING,
        description STRING
    );


    MERGE INTO
        \`${PROJECT_ID}.cme_support.exchanges\` T

    USING
    (
        SELECT
            'CME' AS exchange_code,
            'Chicago Mercantile Exchange' AS exchange_name,
            'Chicago' AS location,
            'Offers futures and options across multiple asset classes.'
            AS description

        UNION ALL

        SELECT
            'CBOT',
            'Chicago Board of Trade',
            'Chicago',
            'Known for agricultural, interest-rate and financial products.'

        UNION ALL

        SELECT
            'NYMEX',
            'New York Mercantile Exchange',
            'New York',
            'Known primarily for energy and commodity products.'

        UNION ALL

        SELECT
            'COMEX',
            'Commodity Exchange',
            'New York',
            'Known primarily for metals futures and options.'

    ) S

    ON T.exchange_code = S.exchange_code


    WHEN MATCHED THEN

        UPDATE SET

            exchange_name =
                S.exchange_name,

            location =
                S.location,

            description =
                S.description


    WHEN NOT MATCHED THEN

        INSERT
        (
            exchange_code,
            exchange_name,
            location,
            description
        )

        VALUES
        (
            S.exchange_code,
            S.exchange_name,
            S.location,
            S.description
        );
    "


echo ""
echo "Exchange table created and populated."


# ==============================================================================
# STEP 4: CREATE EXCHANGE PRODUCTS TABLE
# ==============================================================================

echo ""
echo "============================================================"
echo "Step 4: Creating cme_support.exchange_products"
echo "============================================================"


bq query \
    --nouse_legacy_sql \
    --project_id="$PROJECT_ID" \
    "
    CREATE TABLE IF NOT EXISTS
    \`${PROJECT_ID}.cme_support.exchange_products\`
    (
        exchange_code STRING,
        symbol STRING,
        product_name STRING,
        asset_class STRING
    );


    MERGE INTO
        \`${PROJECT_ID}.cme_support.exchange_products\` T

    USING
    (

        SELECT
            'CME' AS exchange_code,
            'ES' AS symbol,
            'E-mini S&P 500 Futures' AS product_name,
            'Equity Index' AS asset_class

        UNION ALL

        SELECT
            'CME',
            'NQ',
            'E-mini Nasdaq-100 Futures',
            'Equity Index'


        UNION ALL

        SELECT
            'CBOT',
            'ZC',
            'Corn Futures',
            'Agriculture'


        UNION ALL

        SELECT
            'CBOT',
            'ZW',
            'Wheat Futures',
            'Agriculture'


        UNION ALL

        SELECT
            'NYMEX',
            'CL',
            'Crude Oil Futures',
            'Energy'


        UNION ALL

        SELECT
            'NYMEX',
            'NG',
            'Henry Hub Natural Gas Futures',
            'Energy'


        UNION ALL

        SELECT
            'COMEX',
            'GC',
            'Gold Futures',
            'Metals'


        UNION ALL

        SELECT
            'COMEX',
            'SI',
            'Silver Futures',
            'Metals'

    ) S

    ON
        T.exchange_code = S.exchange_code
        AND
        T.symbol = S.symbol


    WHEN MATCHED THEN

        UPDATE SET

            product_name =
                S.product_name,

            asset_class =
                S.asset_class


    WHEN NOT MATCHED THEN

        INSERT
        (
            exchange_code,
            symbol,
            product_name,
            asset_class
        )

        VALUES
        (
            S.exchange_code,
            S.symbol,
            S.product_name,
            S.asset_class
        );
    "


echo ""
echo "Exchange products table created and populated."


# ==============================================================================
# STEP 5: VERIFY DATA
# ==============================================================================

echo ""
echo "============================================================"
echo "Step 5: Verify Exchange Data"
echo "============================================================"


bq query \
    --nouse_legacy_sql \
    --project_id="$PROJECT_ID" \
    "
    SELECT *
    FROM \`${PROJECT_ID}.cme_support.exchanges\`
    ORDER BY exchange_code;
    "


echo ""
echo "============================================================"
echo "Step 6: Verify Exchange Product Data"
echo "============================================================"


bq query \
    --nouse_legacy_sql \
    --project_id="$PROJECT_ID" \
    "
    SELECT *
    FROM \`${PROJECT_ID}.cme_support.exchange_products\`
    ORDER BY exchange_code, symbol;
    "


echo ""
echo "============================================================"
echo "BigQuery Exchange Lab Setup Complete"
echo "============================================================"
echo ""
echo "Dataset:"
echo "  ${PROJECT_ID}.cme_support"
echo ""
echo "Tables:"
echo "  ${PROJECT_ID}.cme_support.exchanges"
echo "  ${PROJECT_ID}.cme_support.exchange_products"
echo ""