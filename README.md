## What have been implemented

- Endless crawling from 6 financial news websites

- News recommendation

- News tagging

- Real time searching

## Installation

- `pip3 install -r requirements.txt`

After setting up the environment successfully, you should run the following three programs step by step, and keep them running simultaneously so that to retrieve newest pages in time.

## Run Crawler

- `python3 crawler.py --kind <kind>`

choices include: "qq", "cnstock", "eastmoney", "sina", "sohu", "tonghuashun"

> Auto save after every 500 pages crawled, so any time to interrupt the program will not hurt, at the next time you run, download will continue from where you interrupt.

## Run json_handler

json_handler transforms html into json format.

- `python3 json_handler.py`

## Run Index Generator

- `python3 engine_test.py`

every time you run this tester, a the search engine will be updated according to the newly crawled pages.

## Run the Website

Running the search engine website, and keep updating its index at the same time.

- `python3 app.py`