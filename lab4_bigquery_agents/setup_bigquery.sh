#!/usr/bin/env bash

# ==============================================================================
# Lab 4 Part 1: BigQuery Dataset, Schema, Table Creation & Data Population
#
# Description:
# 1. Detects active GCP project ID from PROJECT_ID variable or gcloud config.
# 2. Creates BigQuery dataset `cme_support` (US location).
# 3. Creates table schemas: `products`, `market_status`.
# 4. Populates sample data using SQL MERGE statements to ensure idempotency.
# ==============================================================================

set -e

echo "=== Step 1: Validating GCP Project ID ==="
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
  PROJECT_ID=$(gcloud config get-value project 2>/dev/null || true)
fi

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
  echo "Error: PROJECT_ID is not set."
  echo "Please run 'export PROJECT_ID=YOUR_PROJECT_ID' or 'gcloud config set project YOUR_PROJECT_ID' before running this script."
  exit 1
fi

echo "Using GCP Project ID: $PROJECT_ID"

echo ""
echo "=== Step 2: Creating Dataset 'cme_support' ==="
if ! bq show --project_id="$PROJECT_ID" cme_support &>/dev/null; then
  echo "Creating dataset cme_support in US location..."
  bq mk \
    --dataset \
    --location=US \
    --description="Simulated CME support data for Agentic AI training" \
    --project_id="$PROJECT_ID" \
    cme_support
else
  echo "Dataset 'cme_support' already exists."
fi

echo ""
echo "=== Step 3: Creating Schemas, Tables & Merging Data ==="

echo "1. Table Schema & Data: cme_support.products"
bq query \
  --nouse_legacy_sql \
  --project_id="$PROJECT_ID" \
  "
  CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.cme_support.products\` (
    symbol STRING,
    product_name STRING,
    asset_class STRING,
    contract_size STRING,
    currency STRING,
    primary_support_team STRING
  );

  MERGE INTO \`${PROJECT_ID}.cme_support.products\` T
  USING (
    SELECT 'ES' AS symbol, 'E-mini S&P 500 Futures' AS product_name, 'Equity Index' AS asset_class, '\$50 x S&P 500 Index' AS contract_size, 'USD' AS currency, 'Product Support' AS primary_support_team UNION ALL
    SELECT 'NQ', 'E-mini Nasdaq-100 Futures', 'Equity Index', '\$20 x Nasdaq-100 Index', 'USD', 'Market Data Support' UNION ALL
    SELECT 'CL', 'Crude Oil Futures', 'Energy', '1,000 barrels', 'USD', 'Product Support' UNION ALL
    SELECT 'GC', 'Gold Futures', 'Metals', '100 troy ounces', 'USD', 'Product Support'
  ) S
  ON T.symbol = S.symbol
  WHEN MATCHED THEN
    UPDATE SET
      product_name = S.product_name,
      asset_class = S.asset_class,
      contract_size = S.contract_size,
      currency = S.currency,
      primary_support_team = S.primary_support_team
  WHEN NOT MATCHED THEN
    INSERT (symbol, product_name, asset_class, contract_size, currency, primary_support_team)
    VALUES (S.symbol, S.product_name, S.asset_class, S.contract_size, S.currency, S.primary_support_team);
  "

echo "2. Table Schema & Data: cme_support.market_status"
bq query \
  --nouse_legacy_sql \
  --project_id="$PROJECT_ID" \
  "
  CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.cme_support.market_status\` (
    symbol STRING,
    trading_status STRING,
    status_reason STRING,
    last_updated TIMESTAMP
  );

  MERGE INTO \`${PROJECT_ID}.cme_support.market_status\` T
  USING (
    SELECT 'ES' AS symbol, 'TRADING' AS trading_status, 'Market operating normally' AS status_reason UNION ALL
    SELECT 'NQ', 'HALTED', 'Simulated operational halt for training' UNION ALL
    SELECT 'CL', 'TRADING', 'Market operating normally' UNION ALL
    SELECT 'GC', 'CLOSED', 'Market outside simulated trading window'
  ) S
  ON T.symbol = S.symbol
  WHEN MATCHED THEN
    UPDATE SET
      trading_status = S.trading_status,
      status_reason = S.status_reason,
      last_updated = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN
    INSERT (symbol, trading_status, status_reason, last_updated)
    VALUES (S.symbol, S.trading_status, S.status_reason, CURRENT_TIMESTAMP());
  "

echo ""
echo "=== Dataset, Schema, Table Creation & Data Population Complete! ==="
