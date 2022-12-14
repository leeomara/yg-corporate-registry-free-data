# Yukon Corporate Registry data

This project includes a web scraper to extract corporate entity information from the
Yukon Corporate Registry Online (YCOR) website.

YCOR is available at [https://ycor-reey.gov.yk.ca/](https://ycor-reey.gov.yk.ca/)


## What is scraped

Only a subset of freely available data is extracted.

For each corporate entity, I attempt to capture the following fields:

* Registry number
* Name
* Former name (if known)
* Entity type (e.g. "Society")
* Jurisdiction (e.g. "Yukon")
* Status (e.g. "In Compliance")

## Requirements

* [Python](https://www.python.org)
* [Scrapy](https://scrapy.org)

## Install

I've used Poetry to manage dependencies and virtual environments. 

Once you have a copy of this code, running `poetry install` should do the trick, but your
mileage may vary.

## How to use this

Again, I've used Poetry. So start with `poetry shell`

Navigate to `ycor_scraper`.

Run the scraper `scrapy crawl entities`, with options for what capturing results, logging,
etc.

For me, that looks something like:

```
➜ yg-corporate-registry-free-data $ poetry shell
(yg-corporate-registry-free-data-eq4JCDL6-py3.8) ➜  yg-corporate-registry-free-data $ cd ycor_scraper 
(yg-corporate-registry-free-data-eq4JCDL6-py3.8) ➜  ycor_scraper $ scrapy crawl entities --logfile ycor_scraper.log -o ycor_entities.csv
```

## Notes

I am not a python programmer, code and general practices found in this repo may insult
your dog and shouldn't be followed.