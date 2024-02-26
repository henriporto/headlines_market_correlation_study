# Project Overview

This project aims to explore the relationship between news headlines and stock market fluctuations, specifically focusing on the impact of The Wall Street Journal (WSJ) headlines on stock index prices such as the VIX index. By leveraging OpenAI's ChatGPT-4 Turbo, the project develops a systematic approach to analyze how specific news events correlate with changes in stock market volatility and investor sentiment.

## Methodology

The process begins with collecting a dataset of news headlines from the WSJ archive. These headlines serve as input for generating prompts to ChatGPT-4 Turbo, designed to assess the potential impact of each headline on stock market prices. The analysis utilizes a specialized prompt format, which asks the model to predict the direction and magnitude of stock price changes on a scale from 1 to 100 based on the content of the news headline. 

The project further involves a statistical analysis phase, where the generated impact scores from ChatGPT-4 Turbo are correlated with actual market data, specifically the VIX index metrics. This analysis aims to identify patterns and quantify the relationship between news sentiment and market volatility.

## Configuration Instructions

### Editing Database Configuration in `headlines.py`

To specify the database file used by the `headlines.py` script, locate the `DB` variable within the file and modify its value accordingly:

```python
DB = "headlines.db"  # Change "headlines.db" to your database file name
```

### Configuring `chatgpt.py`

The `chatgpt.py` script requires configuring several variables to customize its operation:

- **API Key:** To set the OpenAI API key, edit the `API_KEY` variable. This key can be set in your environment variables. In Windows, you can set it by searching for "Environment Variables" in the Start menu, then clicking on "Edit the system environment variables". Under "System Properties", click on "Environment Variables" and add a new variable with the name `OPENAI_API_KEY` and your API key as the value. On Linux, you can add `export OPENAI_API_KEY='your_api_key_here'` to your `.bashrc` or `.bash_profile` and then run `source ~/.bashrc` or `source ~/.bash_profile`.

- **GPT Model:** Change the GPT model by editing the `GPT_MODEL` variable. Supported models include `"gpt-3.5-turbo"` and `"gpt-4-0125-preview"`.

```python
GPT_MODEL = "gpt-3.5-turbo"  # or "gpt-4-0125-preview"
```

- **Adjusting Stock Index, Token Costs, and Other Parameters:** Fine-tune the script's settings by specifying the stock index for analysis, input and output token costs, the maximum number of retries for incorrect GPT outputs, the database filename, the GPT API endpoint, and the request rate limit per minute. Note that the feature to limit tokens per minute (TPM) has not yet been implemented.

```python
STOCK_INDEX = "CBOE Volatility Index"
TOKEN_COST_1_INPUT = Decimal("0.00001")
TOKEN_COST_1_OUTPUT = Decimal("0.00003")
GPT_RETRY_WRONG_OUTPUT_LIMIT = 1000
DB = "headlines_only3.db"
GPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
GPT_REQUESTS_PER_MINUTE = 3
getcontext().prec = 20
```

- **Prompt Variable:** To change the prompt used in the script, edit the variable at line 313.

```python
input_text = "your_custom_prompt_here"  # Edit your prompt here
```

## Usage Instructions

1. **Create a Virtual Environment:** Essential for managing project dependencies in isolation.

```bash
# For Windows
python -m venv myenv
myenv\Scripts\Activate

# For macOS and Linux
python3 -m venv myenv
source myenv/bin/activate
```

2. **Install Requirements:** Install the necessary Python packages to ensure the scripts run smoothly.

```bash
python -m pip install -r requirements.txt
```

3. **Get Headlines from WSJ Archive and Insert in DB:** Fetch and store WSJ headlines in a database for analysis.

```bash
python headlines.py
```

4. **Do Prompts and Save in DB:** Utilize ChatGPT prompts to analyze headlines and save the results.

```bash
python chatgpt.py
```

5. **Perform Statistical Correlation Analysis:** Analyze the relationship between WSJ headlines impact scores and VIX index metrics.

```bash
python correlation_analysis.py
```

This step involves comprehensive data handling and statistical calculations to derive meaningful insights about the correlation between news sentiment and market behavior.


## Specialized ChatGPT Prompt

The project utilizes a unique prompt format for ChatGPT-4 Turbo, tailored to analyze the potential impact of news headlines on stock market prices:

```plaintext
Forget all previous instructions. You are now a financial expert analyzing the stock market in {month}/{year}. Upon receiving a news headline, assess its impact on {STOCK_INDEX} prices. Predict whether the headline suggests a rise or drop in prices by providing a number on a scale from 1 to 100, where 1 signifies a significant decrease, 100 signifies a significant increase, and 50 indicates uncertainty. Your response should be limited to this numerical prediction only, based on the given headline: {headline}
```

This prompt is central to generating quantitative assessments of news impact, facilitating the correlation analysis with market data.