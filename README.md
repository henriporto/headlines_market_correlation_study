# Setup Guide

## Create a Virtual Environment
To manage project dependencies, create a virtual environment:

```bash
# For Windows
python -m venv myenv
myenv\Scripts\Activate

# For macOS and Linux
python3 -m venv myenv
source myenv/bin/activate
```

## Install Requirements
Next, install the necessary Python packages:
- `pip install -r requirements.txt`

## Get Headlines from WSJ Archive and Insert in DB
Run the script to fetch headlines from the WSJ archive and insert them into the database:
- `python headlines2.py`

## Do Prompts and Save in DB
Execute the script to use ChatGPT prompts and save the responses in the database:
- `python chatgpt.py`

## Perform Statistical Correlation Analysis
To understand the relationship between the impact scores of WSJ headlines and various VIX index metrics, execute the `correlation_analysis.py` script. This will calculate statistical correlations and save the results in a PDF file:

- `python correlation_analysis.py`

This script performs a comprehensive data analysis, from reading and preparing the data, through statistical analysis, to visualizing the results. It involves connecting to a SQLite database to fetch headlines data, loading and preparing VIX index data from a CSV file, calculating Pearson correlation coefficients and linear regressions, and saving plots of these analyses in a PDF document.

Ensure you have the `headlines.db` and `VIX.csv` files correctly placed in your project directory as specified by the `correlation_analysis.py` script.