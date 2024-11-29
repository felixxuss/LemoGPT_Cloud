from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import *

# load the environment variables
load_dotenv()


class LemoAgent:
    def __init__(self, model, start_year, end_year, verbose=False):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.verbose = verbose
        self.model = model
        self.start_year = start_year
        self.end_year = end_year

        self.year_summaries = {}

        # total token usage
        self.total_tokens_in = 0
        self.total_tokens_out = 0

        self.set_prices()

    def query(self, question):
        # summarize context with LLM
        answer, price = self.summarize_context(question)

        # print price
        print(f"Estimated price: {price:.2f} Cent")

        return answer, price

    def set_prices(self):
        # set prices
        if self.model == "gpt-4o-mini":
            self.in_price = 0.15  # per 1M tokens
            self.out_price = 0.6  # per 1M tokens
        elif self.model == "gpt-4o":
            self.in_price = 5  # per 1M tokens
            self.out_price = 15  # per 1M tokens
        else:
            raise ValueError("Model not supported")

    def get_context(self, question):
        for year in range(self.start_year, self.end_year + 1):
            with open(f"data/chronical_text_{year}.txt", "r") as f:
                context = f.read()

            prompt = summary_prompt_template.format(
                year=year, context=context, question=question
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": summary_system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            # completion_tokens, prompt_tokens
            self.total_tokens_in += response.usage.prompt_tokens
            self.total_tokens_out += response.usage.completion_tokens

            content = response.choices[0].message.content
            self.year_summaries[str(year)] = content

            if self.verbose:
                print(f"\n\nRelevant context from year {year}:")
                print(content)
                print("\n\n")
            yield year

    def format_save_content(self, question, answer, price):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{dt_string}_{self.start_year}_{self.end_year}.txt"

        text = f"Model: {self.model}\n\nFrage:\n\n{question}\n\n\nKontext:\n{self.relevant_context}\n\n\nAntwort:\n\n{answer}\n\n\nPreis:\n\n{price:.2f} Cent"
        return text, file_name

    def save_answer_old(self, question, answer, price):
        # price in cent
        # get current dayte and time like this: YYYY-MM-DD_HH-MM-SS
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"/answers/{dt_string}_{self.start_year}_{self.end_year}.txt"
        text = f"Model: {self.model}\n\nFrage:\n\n{question}\n\n\nKontext:\n{self.relevant_context}\n\n\nAntwort:\n\n{answer}\n\n\nPreis:\n\n{price:.2f} Cent"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(text)

    def summarize_context(self, question):
        # combine year summaries in one text
        self.relevant_context = ""
        for year, summary in self.year_summaries.items():
            self.relevant_context += f"\n\nJahr {year}:\n {summary}"

        if self.verbose:
            print("\n\nRelevant context:")
            print(self.relevant_context)
            print("\n\n")

        final_prompt = final_prompt_template.format(
            context=self.relevant_context, question=question
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": final_prompt},
            ],
        )

        self.total_tokens_in += response.usage.prompt_tokens
        self.total_tokens_out += response.usage.completion_tokens

        price_final = (self.total_tokens_in / 1e6 * self.in_price) + (
            self.total_tokens_out / 1e6 * self.out_price
        ) * 100  # in cent

        content = response.choices[0].message.content

        return content, price_final
