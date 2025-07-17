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
# domain GitBook
# -------------------------------
if [[ "$1" == "domain-gitbook" ]]; then
  echo "📘 Building domain GitBook..."
  cp -f index-domain-gitbook.Rmd index.Rmd
  link_bookdown_config _bookdown-domain.yml

  mkdir -p docs
  Rscript -e 'bookdown::render_book("index.Rmd", "bookdown::gitbook", output_dir = "docs")'

  rm index.Rmd
  echo "✅ domain GitBook complete → /docs"


# -------------------------------
# domain PDF
# -------------------------------
elif [[ "$1" == "domain-bs4" ]]; then
  echo "📘 Building domain bs4..."
  cp -f index-domain-bs4.Rmd index.Rmd
  link_bookdown_config _bookdown-domain.yml
  mkdir -p domain-bs4
  Rscript -e 'bookdown::render_book("index.Rmd", "bookdown::bs4_book", output_dir = "domain-bs4")'
  rm index.Rmd
  echo "✅ domain bs4 complete → /domain-bs4"


# -------------------------------
# domain BS4
# -------------------------------
elif [[ "$1" == "domain-pdf" ]]; then
  echo "📘 Building domain PDF..."
  cp -f index-domain-pdf.Rmd index.Rmd
  link_bookdown_config _bookdown-domain.yml
  mkdir -p domain-pdf
  Rscript -e 'bookdown::render_book("index.Rmd", "bookdown::pdf_book", output_dir = "domain-pdf")'
  rm index.Rmd
  echo "✅ domain PDF complete → /domain-pdf"




# -------------------------------
# Help / fallback
# -------------------------------
else
  echo "❌ Unknown build option: $1"
  exit 1
fi
