#!/bin/bash

# Exit immediately if any command fails
set -e

# Print the current R version (useful for logging and debugging)
echo "📦 R version:"
Rscript -e 'R.version.string'

# Function to link the correct Bookdown YAML config file
# Arguments:
#   $1 - The config filename to use (e.g., _bookdown-viz-gwas.yml)
link_bookdown_config() {
  local config="$1"
  echo "🔧 Using config: $config"

  # Create or update a symbolic link named _bookdown.yml pointing to the desired config
  cp -f "$config" _bookdown.yml
}

# -------------------------------
# model-deployment GitBook
# -------------------------------
if [[ "$1" == "model-deployment-gitbook" ]]; then
  echo "📘 Building model-deployment GitBook..."
  cp -f index-model-deployment-gitbook.Rmd index.Rmd
  link_bookdown_config _bookdown-model-deployment.yml

  mkdir -p docs
  Rscript -e 'bookdown::render_book("index.Rmd", "bookdown::gitbook", output_dir = "docs")'

  rm index.Rmd
  echo "✅ model-deployment GitBook complete → /docs"


# # -------------------------------
# # model-deployment PDF
# # -------------------------------
# elif [[ "$1" == "model-deployment-bs4" ]]; then
#   echo "📘 Building model-deployment bs4..."
#   cp -f index-model-deployment-bs4.Rmd index.Rmd
#   link_bookdown_config _bookdown-model-deployment.yml
#   mkdir -p model-deployment-bs4
#   Rscript -e 'bookdown::render_book("index.Rmd", "bookdown::bs4_book", output_dir = "model-deployment-bs4")'
#   rm index.Rmd
#   echo "✅ model-deployment bs4 complete → /model-deployment-bs4"


# # -------------------------------
# # model-deployment BS4
# # -------------------------------
# elif [[ "$1" == "model-deployment-pdf" ]]; then
#   echo "📘 Building model-deployment PDF..."
#   cp -f index-model-deployment-pdf.Rmd index.Rmd
#   link_bookdown_config _bookdown-model-deployment.yml
#   mkdir -p model-deployment-pdf
#   Rscript -e 'bookdown::render_book("index.Rmd", "bookdown::pdf_book", output_dir = "model-deployment-pdf")'
#   rm index.Rmd
#   echo "✅ model-deployment PDF complete → /model-deployment-pdf"




# -------------------------------
# Help / fallback
# -------------------------------
else
  echo "❌ Unknown build option: $1"
  exit 1
fi
