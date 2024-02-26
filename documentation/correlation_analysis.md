# Headline Impact and VIX Correlation Analysis

The `correlation_analysis.py` Python script analyzes the correlation between the sentiment of Wall Street Journal headlines and the closing values of the VIX index, over a specified period. The analysis involves fetching headline scores from a database, adjusting and aggregating these scores by day, correlating the aggregated scores with daily VIX index closing values, and generating visual reports to illustrate the findings.

## Dependencies

- sqlite3
- pandas
- matplotlib
- fpdf
- numpy
- scipy.stats

## Database and File Setup

- **DB_PATH:** Path to the SQLite database containing headlines and their sentiment scores.
- **VIX_CSV_PATH:** Path to the CSV file containing daily VIX index closing values.

## Batch Processing

To manage memory efficiently, the script processes data in batches, defined by `BATCH_SIZE`.

## Functions

### fetch_headline_scores

Fetches headlines and their GPT output scores from the database in batches for memory efficiency.

### adjust_and_aggregate_scores

Adjusts the fetched scores based on a predefined criteria (subtracting 50 from each score) and aggregates these adjusted scores by day.

### read_vix_data

Reads the VIX index data from a CSV file and formats the date column for easy comparison with the headline data.

### correlate_data

Correlates the adjusted and aggregated daily scores with the VIX index data, ensuring that only days with both scores and VIX data are included in the analysis.

### generate_plots_and_reports

Generates a scatter plot for the daily scores versus VIX Close data, including a line of best fit, correlation statistics, and hypothesis testing results. It also generates a PDF report containing the plot and key statistics.

## Main Execution

The `main` function orchestrates the execution of the script, from data fetching and processing to correlation analysis and report generation.

## Usage

To run the analysis, ensure that the SQLite database and the VIX CSV file are correctly set up and accessible. Then execute the script:

```bash
python script_name.py
```

The script will generate a scatter plot image and a PDF report detailing the daily headline scores versus VIX Close correlation, including statistical analysis results.

## Output

- **Image File:** 'scores_vs_vix_close_with_line_and_stats.png'
- **PDF Report:** 'report_scores_vs_vix_with_line_and_stats.pdf'

The output provides a visual and statistical analysis of the correlation between Wall Street Journal headline sentiment and market volatility, as measured by the VIX index.