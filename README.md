# Project Overview

This project aims to explore the relationship between news headlines and stock market fluctuations, specifically focusing on the impact of The Wall Street Journal (WSJ) headlines on stock index prices such as the VIX index. By leveraging OpenAI's ChatGPT-4 Turbo, the project develops a systematic approach to analyze how specific news events correlate with changes in stock market volatility and investor sentiment.

## Methodology

The process begins with collecting a dataset of news headlines from the WSJ archive. These headlines serve as input for generating prompts to ChatGPT-4 Turbo, designed to assess the potential impact of each headline on stock market prices. The analysis utilizes a specialized prompt format, which asks the model to predict the direction and magnitude of stock price changes on a scale from 1 to 100 based on the content of the news headline. 

The project further involves a statistical analysis phase, where the generated impact scores from ChatGPT-4 Turbo are correlated with actual market data, specifically the VIX index metrics. This analysis aims to identify patterns and quantify the relationship between news sentiment and market volatility.

## Implementation Steps

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
   pip install -r requirements.txt
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
```