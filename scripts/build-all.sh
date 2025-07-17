#!/bin/bash

set -e

total_start=$(date +%s)  # ⬅️ Start total timer


# Define the list of Jupyter Notebook filenames (without extension)
NOTEBOOK_NAMES=(
    "01-1-model-deployment"
)

# Define the output directory (use current folder)
OUTPUT_DIR="./"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Loop through each notebook
for NOTEBOOK_NAME in "${NOTEBOOK_NAMES[@]}"; do
    if [[ ! -f "$NOTEBOOK_NAME.ipynb" ]]; then
        echo "❌ $NOTEBOOK_NAME.ipynb not found. Skipping..."
        continue
    fi

    echo "⚙️  Executing and converting: $NOTEBOOK_NAME.ipynb"

    # Step 1: Execute and convert notebook to Markdown with outputs
    jupyter nbconvert --to markdown --execute \
        --ExecutePreprocessor.timeout=300 \
        --output-dir "$OUTPUT_DIR" \
        "$NOTEBOOK_NAME.ipynb"

    # Step 2: Rename .md to .Rmd
    if [[ -f "$OUTPUT_DIR/$NOTEBOOK_NAME.md" ]]; then
        mv "$OUTPUT_DIR/$NOTEBOOK_NAME.md" "$OUTPUT_DIR/$NOTEBOOK_NAME.Rmd"
        echo "✅ Converted: $NOTEBOOK_NAME.Rmd"
    else
        echo "⚠️  Warning: $NOTEBOOK_NAME.md not found. Skipping rename."
        continue
    fi

    # Step 3: Fix image tag formatting if needed
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/!\[png\]/![]/g' "$OUTPUT_DIR/$NOTEBOOK_NAME.Rmd"
    else
        sed -i 's/!\[png\]/![]/g' "$OUTPUT_DIR/$NOTEBOOK_NAME.Rmd"
    fi
done


echo "🚀 Starting full build for all types of BOOKDOWN reports..."

levels=("model-deployment-gitbook")
for level in "${levels[@]}"; do
  echo ""
  echo "🔁 Building: $level"
  bash ./scripts/build-configurable.sh "$level"
done

echo ""
echo "✅ All levels built successfully."

echo "🧹 Cleaning up intermediate build files..."
rm -f *-pdf/*.md *-pdf/*.tex
rm -f *-pdf/*.md *-pdf/*.tex
rm -rf *-pdf/_bookdown_files/
rm -rf *-pdf/_bookdown_files/
rm -f ./*.rds
echo "✅ Cleanup complete."

# Remove symlink to avoid accidental reuse
rm -f index.Rmd
rm -f _bookdown.yml


total_end=$(date +%s)
total_elapsed=$((total_end - total_start))
minutes=$((total_elapsed / 60))
seconds=$((total_elapsed % 60))

echo -e "\n⏱️  Total build time: ${minutes} min ${seconds} sec"
