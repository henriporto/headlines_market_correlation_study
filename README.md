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
