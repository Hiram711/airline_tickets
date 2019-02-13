# Airline_Tickets

## Introduction
This project is aimed to crawl the detail price info from airlines' official websites by scrapy.

## Quick Start
> The project supports both Linux and Windows operation system
> The following scripts can be executed under Linux and Windows
* Clone the project
```bash
git clone https://github.com/Hiram711/airline_tickets.git
```
* Build a virtualenv and activate it
```bash
cd airline_tickets
virtualenv venv
cd venv/Scripts
# when under Linux,should be ./activate
activate
```
* Install the dependencies in the virtualenv
```bash
pip install -r requirements.txt
```
* Create database and tables
```bash
cd ..
python airline_tickets/models.py
```
* Run
```bash
python main.py
```

## Crawled Airlines
* MU

## To Do

### Airlines to be crawled
* CZ
* 9C
* HO
* HU
* KY
* 3U
* 8L

### Improve
* Build the proxy pool
* Log the crawling segments failed error into the database
* Import Scrapy-Redis to realize distributed crawler
* Replace the Selenium downloader middleware with Puppeteer(now there is some bugs in Pyppeteer)
* Import Scrapyd
