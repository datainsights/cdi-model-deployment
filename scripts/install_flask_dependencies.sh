#!/bin/bash

# Define required Python libraries
REQUIRED_LIBRARIES=("flask" "joblib" "numpy" "pandas" "scikit-learn")

# Function to check if a library is installed
check_and_install() {
    LIBRARY=$1
    # Use Python to test library availability
    python3 -c "import importlib; assert importlib.util.find_spec('$LIBRARY')" &> /dev/null
    if [ $? -eq 0 ]; then
        echo "$LIBRARY is already installed."
    else
        echo "$LIBRARY is not installed. Installing..."
        python3 -m pip install $LIBRARY
    fi
}

# Ensure pip is up to date
echo "Ensuring pip is up-to-date..."
python3 -m pip install --upgrade pip

# Check and install required libraries
for LIBRARY in "${REQUIRED_LIBRARIES[@]}"
do
    check_and_install $LIBRARY
done

echo "All required libraries are installed!"