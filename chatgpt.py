from openai import OpenAI
import os
import tiktoken
import sqlite3
from decimal import Decimal, getcontext
from tenacity import retry, stop_after_attempt, wait_random_exponential
from datetime import datetime, timedelta
import time
import requests
import re
import sys
import argparse

# Create the parser
parser = argparse.ArgumentParser()
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Increase output verbosity"
)
parser.add_argument(
    "-c", "--calculate", action="store_true", help="Calculate Total Tokens and Price"
)
args = parser.parse_args()

## TODO: organize with classes

API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-3.5-turbo"  # "gpt-4-0125-preview"
STOCK_INDEX = "CBOE Volatility Index"
TOKEN_COST_1_INPUT = Decimal("0.00001")  # Dollar
TOKEN_COST_1_OUTPUT = Decimal("0.00003")
GPT_RETRY_WRONG_OUTPUT_LIMIT = 1000
DB = "headlines_only3.db"
GPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
GPT_REQUESTS_PER_MINUTE = 3
getcontext().prec = 20
request_counters = {
    "limit_requests": 60,
    "limit_tokens": 150000,
    "remaining_requests": 60,
    "remaining_tokens": 150000,
    "reset_requests": datetime.now() + timedelta(seconds=1),
    "reset_tokens": datetime.now() + timedelta(minutes=6),
}
rpm_next_time = Decimal(0)
last_request_time = datetime.now().strftime("%H:%M:%S")


def convert_reset_time_to_seconds(time_str):
    if args.verbose:
        print("Em: ", "convert_to_seconds")
    # This pattern will match hours, minutes, and seconds in the input string
    pattern = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?"
    match = re.search(pattern, time_str)

    if match is None or match.group(0) == '':
        return False
    
    hours, minutes, seconds = match.groups(default="0")
    # Convert all to seconds and sum them up
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    return total_seconds


def update_rate_limit_counters(headers):
    if args.verbose:
        print("Em: ", "update_rate_limit_counters")
    global request_counters
    try:
        request_counters["limit_requests"] = int(
            headers.get("x-ratelimit-limit-requests", 60)  # rpd
        )
        request_counters["limit_tokens"] = int(
            headers.get("x-ratelimit-limit-tokens", 150000)  # tpd
        )
        request_counters["remaining_requests"] = int(
            headers.get("x-ratelimit-remaining-requests", 60)  # remaining rpd
        )
        request_counters["remaining_tokens"] = int(
            headers.get("x-ratelimit-remaining-tokens", 150000)  # remaining tpd
        )
        reset_requests_seconds = int(
            convert_reset_time_to_seconds(
                headers.get("x-ratelimit-reset-requests", "1s")
            )
        )
        reset_tokens_seconds = int(
            convert_reset_time_to_seconds(
                headers.get("x-ratelimit-reset-tokens", "360s")
            )
        )
        request_counters["reset_requests"] = datetime.now() + timedelta(
            seconds=reset_requests_seconds
        )
        request_counters["reset_tokens"] = datetime.now() + timedelta(
            seconds=reset_tokens_seconds
        )
    except Exception as e:
        print(f"Warning: Error in rate-limit headers: {headers}. Error: {e}")


def wait_for_rate_limit_reset():
    if args.verbose:
        print("Em: ", "wait_for_rate_limit_reset")
    """Wait until the rate limit resets."""
    global request_counters
    now = datetime.now()

    wait_seconds_requests = (request_counters["reset_requests"] - now).total_seconds()
    wait_seconds_tokens = (request_counters["reset_tokens"] - now).total_seconds()
    wait_seconds = (
        wait_seconds_requests
        if wait_seconds_requests > wait_seconds_tokens
        else wait_seconds_tokens
    )

    if wait_seconds > 0:
        print(
            f"Rate limit exceeded. Waiting for {wait_seconds} seconds until limit resets."
        )
        time.sleep(wait_seconds)


def log_retry_failure(retry_state): # Define a callback function for retry errors to log the details
    if args.verbose:
        print("Em: ", "log_retry_failure")
    last_exception = retry_state.outcome.exception()
    if last_exception and hasattr(last_exception, "response"):
        response = last_exception.response
        print(
            f"Retry stopped after {retry_state.attempt_number} attempts. Last response status code: {response.status_code}, Headers: {response.headers}"
        )
    else:
        print(
            f"Retry stopped after {retry_state.attempt_number} attempts. No response available."
        )


@retry(
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(10),
    retry_error_callback=log_retry_failure,
)
def attempt_fetch_completion(messages):
    global last_request_time
    if args.verbose:
        print("Em: ", "attempt_fetch_completion")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": GPT_MODEL,
        "messages": messages,
    }
    response = requests.post(GPT_ENDPOINT, json=data, headers=headers)
    last_request_time = datetime.now().strftime("%H:%M:%S")
    update_rate_limit_counters(
        response.headers
    )  # Update rate limit counters based on the response headers
    return response.json()


def fetch_completion(messages):
    if args.verbose:
        print("Em: ", "fetch_completion")

    tokens_needed = num_tokens_from_messages(messages)

    # Checking remaining tokens with headers data
    if (
        request_counters["remaining_tokens"] < tokens_needed
        or request_counters["remaining_requests"] <= 0
    ):
        wait_for_rate_limit_reset()

    json_response = attempt_fetch_completion(messages)
    
    return json_response


def make_request_with_rate_limit(messages):
    global rpm_next_time

    rps = Decimal(GPT_REQUESTS_PER_MINUTE) / Decimal(60)  # Requests per second (RPM / 60)
    interval = Decimal(1) / rps  # Interval between requests

    if rpm_next_time == Decimal(0):
        rpm_next_time = Decimal(time.time()) + interval

    now = Decimal(time.time())
    if now >= rpm_next_time:
        json_response = fetch_completion(messages)  # Your existing request function
        rpm_next_time = now + interval
        delay_correction = rpm_next_time - Decimal(time.time())
        if delay_correction > 0:
            time.sleep(float(delay_correction))  # Sleep to adjust the request rate
        return json_response
    else:
        # Delay until the next calculated time if called too early
        time.sleep(float(rpm_next_time - now))
        return make_request_with_rate_limit(messages)


def num_tokens_from_messages(messages):
    if args.verbose:
        print("Em: ", "num_tokens_from_messages")
    try:
        encoding = tiktoken.encoding_for_model(GPT_MODEL)
    except ValueError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0

    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def num_tokens_from_string(string: str) -> int:
    if args.verbose:
        print("Em: ", "num_tokens_from_string")
    try:
        encoding = tiktoken.encoding_for_model(GPT_MODEL)
    except ValueError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def calculate_cost(input_message, output_text):
    if args.verbose:
        print("Em: ", "calculate_cost")
    input_cost = num_tokens_from_messages(input_message) * TOKEN_COST_1_INPUT
    output_cost = num_tokens_from_string(output_text) * TOKEN_COST_1_OUTPUT

    total_cost = input_cost + output_cost
    return total_cost


def get_headlines_by_year(cursor):
    if args.verbose:
        print("Em: ", "get_headlines_by_year")
    query = "SELECT id, strftime('%Y', ydm) AS year, strftime('%m', ydm) AS month, headline FROM headlines ORDER BY ydm ASC"
    cursor.execute(query)
    row_count = 0  # Debugging
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_count += 1  # Debugging
        yield row


def insert_output_data(conn, id, output_text):
    if args.verbose:
        print("Em: ", "insert_output_data")
    local_cursor = conn.cursor()
    local_cursor.execute(
        "UPDATE headlines SET output = ? WHERE id = ?", (output_text, id)
    )


def is_response_ok(completion):
    try:
        output_text = completion["choices"][0]["message"]["content"]
        ok = True
    except Exception as e:
        if (
            "error" in completion
            and "message" in completion["error"]
            and "Rate limit" in completion["error"]["message"]
        ):            
            time_raw = re.search(r"(?<=Please try again in ).*?(?=\. Visit)", completion["error"]["message"]).group(0)
            if args.verbose:
                print("is_response_ok(), time_raw: ", time_raw)
            match = convert_reset_time_to_seconds(time_raw)
            if args.verbose:
                print("is_response_ok(), match: ", match)
            print(f"Warning: Error in response: {completion}. Error: {e}")
            if match and isinstance(match, float):
                print(f"Sleeping time: {match}")
                time.sleep(match)
            else:
                msg = input("Deseja parar o programa? (s/n)").lower()
                if msg == "s" or msg == "sim":
                    sys.exit()
        output_text = ""
        ok = False
    return output_text, ok


def main():
    cost = Decimal("0")
    done_count = 0
    
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        for id, year, month, headline in get_headlines_by_year(cursor):
            if args.verbose:
                print("Em: ", "for id, year, month, headline")
            retry_count_wrong_output = 0
            while True:
                input_text = f"Forget all previous instructions. You are now a financial expert analyzing the stock market in {month}/{year}. Upon receiving a news headline, assess its impact on {STOCK_INDEX} prices. Predict whether the headline suggests a rise or drop in prices by providing a number on a scale from 1 to 100, where 1 signifies a significant decrease, 100 signifies a significant increase, and 50 indicates uncertainty. Your response should be limited to this numerical prediction only, based on the given headline: {headline}"
                messages = [{"role": "system", "content": input_text}]
                completion = make_request_with_rate_limit(messages)
                output_text, ok = is_response_ok(completion)
                if not ok:
                    continue # Continua o loop para tentar novamente
                try:
                    number = int(output_text)
                    if 1 <= number <= 100:
                        insert_output_data(conn, id, number)
                        done_count += 1
                        break
                    else:
                        if retry_count_wrong_output >= GPT_RETRY_WRONG_OUTPUT_LIMIT:
                            print(f"O GPT_RETRY_WRONG_OUTPUT_LIMIT = {GPT_RETRY_WRONG_OUTPUT_LIMIT} foi atingido!\n")
                            break
                        raise ValueError
                except ValueError:
                    retry_count_wrong_output += 1
                    print(
                        f"\rNúmero inválido recebido. Tentando novamente... Tentativa: {retry_count_wrong_output}",
                        end="",
                    )
                    continue  # Continua o loop para tentar novamente

            cost += calculate_cost(messages, output_text)
            print(
                f"\rCOMPLETED: {done_count} - TOTAL COST: ${cost} - WRONG OUTPUTS: {retry_count_wrong_output} - LAST REQUEST TIME: {last_request_time}. ",
                end="",
            )


if __name__ == "__main__":
    main()
