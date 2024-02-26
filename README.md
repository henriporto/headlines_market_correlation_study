# NewsVestor Analytics: Unveiling the Impact of WSJ Headlines on Market Volatility

## Project Overview

This project aims to explore the relationship between news headlines and stock market fluctuations. While initially focusing on the significant influence of The Wall Street Journal (WSJ) headlines, our scope extends to encompass a wider array of news sources. This inclusive approach allows us to capture a broader spectrum of market sentiments and their impacts on stock index prices, particularly the VIX index. Leveraging the advanced capabilities of OpenAI's ChatGPT-4 Turbo, NewsVestor Analytics employs a systematic methodology to unravel the correlation between diverse news events and shifts in stock market volatility and investor sentiment.


## Methodology

For each headline, ChatGPT-4 assigns an impact score from 1 to 100, where:
- **50** means the news is neutral, with no expected impact on stock prices.
- **Scores above 50** indicate a positive impact, predicting a potential increase in stock prices.
- **Scores below 50** signal a negative impact, suggesting a possible decrease in stock prices.

This straightforward scoring system quantifies the potential influence of news on market dynamics, serving as a foundation for correlating these predictions with actual market behavior.

## Correlation Analysis Documentation

For a detailed explanation of the correlation analysis methodology and findings, refer to the [Correlation Analysis Documentation](documentation/correlation_analysis.md).

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