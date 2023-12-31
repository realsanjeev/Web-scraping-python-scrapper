# Scrapy

### Start scrapy project
''''Problem may rise if you are using github global env. Create virtual env to run scrapy without problem''
```
scrapy startproject <projectname>
```
### For interactive shell
```
pip install ipython
```

### Run scrapy pogram
```
cd <projectname>
scrapy genspider bookspider books.toscrape.com
scrapy crawl bookspider
```
Sample file for `bookscrape.py`
```python
import scrapy

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('.product_pod')
        for book in books:
            yield {
                'name': book.css('h3 a::text').get(),
                'price': book.css('.product_price .price_color::text').get(),
                'url': book.css('h3 a').attrib['href']
            }
        
        next_page = response.css('.pager li.next a::attr("href")').get()
        if next_page is not None:
            next_page= 'catalogue/' + next_page if 'catalogue' not in next_page else  next_page
            next_page_url = "https://books.toscrape.com/" + next_page
            yield response.follow(next_page_url, callback=self.parse)
```
### To save scraped data in file
1. Rewrite file every time you scrapy
```
$ scrapy crawl bookspider -O data.csv
```
2. Append the data in same file
```
$ scrapy crawl bookspider -0 data.csv
```
3. You can specify the way file is scrape in `settings.py`
```
FEEDS = {
    'book.json': {'format': 'json'}
}
```
Run scrapy as usual. It saves file in `data.json`
```
$ scrapy crawl bookspider
```

For database installation. See: [DATABASE-CMD.md](https://github.com/realsanjeev/Book-scraping-python-scapper/blob/main/DATABASE-CMD.md)

## Python package manager for mySql
```
pip install mysql-connector-python
```
Create a database and proceed. Change database name in `bookscrape/bookscrape/pipeline.py` `SaveToMySQLPipeline` to your database
## For rotating proxy
```
pip install scrapy-rotating-proxies
```

##### For config env variable


