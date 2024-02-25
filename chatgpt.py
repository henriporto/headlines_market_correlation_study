from openai import OpenAI
import os
import tiktoken
import sqlite3
from decimal import Decimal, getcontext

API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4-0125-preview"
STOCK_INDEX = "CBOE Volatility Index"
TOKEN_COST_1_INPUT = Decimal("0.00001")  # Dolar
TOKEN_COST_1_OUTPUT = Decimal("0.00003")
RETRY_COUNT_LIMIT = 1000
DB = "headlines.db"
getcontext().prec = 12


def num_tokens_from_messages(messages):
    try:
        encoding = tiktoken.encoding_for_model(GPT_MODEL)
    except KeyError:
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


def calculate_cost(input_text, output_text):
    input_cost = num_tokens_from_messages(input_text) * TOKEN_COST_1_INPUT
    output_cost = num_tokens_from_messages(output_text) * TOKEN_COST_1_OUTPUT

    total_cost = input_cost + output_cost
    return total_cost


def get_headlines_by_year():
    # Conectar ao banco de dados SQLite
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        # Executar a consulta SQL para selecionar o ano e a manchete, ordenados pela data
        query = "SELECT id, strftime('%Y', ydm) AS year, strftime('%m', ydm) AS month, headline FROM headlines ORDER BY ydm ASC"
        cursor.execute(query)
        # Usar fetchone() em um loop para iterar sobre cada registro individualmente
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row


def insert_output_data(headline, id, output_text):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE headlines SET output = ? WHERE id = ?", (output_text, id)
        )


def main():

    client = OpenAI(api_key=API_KEY)
    cost = Decimal("0")

    for id, year, month, headline in get_headlines_by_year():
        retry_count = 0
        while True:
            input_text = f"Forget all previous instructions. You are now a financial expert analyzing the stock market in {month}/{year}. Upon receiving a news headline, assess its impact on {STOCK_INDEX} prices. Predict whether the headline suggests a rise or drop in prices by providing a number on a scale from 1 to 100, where 1 signifies a significant decrease, 100 signifies a significant increase, and 50 indicates uncertainty. Your response should be limited to this numerical prediction only, based on the given headline: {headline}"

            completion = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": input_text},
                ],
            )

            output_text = completion.choices[0].message.content.strip()
            try:
                number = int(output_text)
                if 1 <= number <= 100:
                    insert_output_data(headline, id, number)
                    break
                else:
                    if retry_count >= RETRY_COUNT_LIMIT:
                        print(f"RETRY_COUNT_LIMIT atingido!\n")
                        break
                    raise ValueError
            except ValueError:
                retry_count += 1
                print(
                    f"\rNúmero inválido recebido. Tentando novamente... Tentativa: {retry_count}",
                    end="",
                )
                continue  # Continua o loop para tentar novamente

        cost += calculate_cost(input_text, output_text)
        print(f"\rCUSTO TOTAL: ${cost} (Tentativas: {retry_count})", end="")


if __name__ == "__main__":
    main()
