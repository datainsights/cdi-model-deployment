#!/bin/bash
set -e

# 🧠 Prompt for domain only if not set externally
if [ -z "$CDI_DOMAIN" ]; then
  read -p "Enter domain (e.g., general-ds, microbiome): " CDI_DOMAIN
fi

export CDI_DOMAIN

echo "🔁 Starting R package installation..."
Rscript scripts/cdi-install-packages.R
echo "✅ R package installation complete."

# 🔄 Restore renv environment if lockfile exists
if [ -f renv.lock ]; then
  echo "🔄 Restoring R packages from renv.lock..."
  Rscript -e 'renv::restore()'
  echo "✅ renv environment restored."
else
  echo "⚠️ renv.lock not found. Skipping restore."
fi