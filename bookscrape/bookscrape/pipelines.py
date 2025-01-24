# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#
# useful for handling different item types with a single interface
import os
from itemadapter import ItemAdapter
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# config variable
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "scraper_db")

class BookscrapePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item=item)

        # strip all trailing and leading whitespaces from strings in value if any
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if value:
                adapter[field_name] = value.strip()
        
        # convert value of genre and type to lowercase
        lowercase_keys = ['genre', 'type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            if value:
                adapter[lowercase_key] = value.lower()

        # get availability in number of stock
        availability_key = 'availability'
        availability_value = adapter.get(availability_key)
        if availability_value:
            split_string_array = availability_value.split("(")
            if (len(split_string_array) < 2):
                adapter[availability_key] = int(0)
            else:
                adapter[availability_key] = int(split_string_array[1].split()[0])
        else:
             adapter[availability_key] = 0
        
        
        # price(str) --> convert to float
        price_keys = ['price', 'price_incl_tax', 'price_excl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if value:
                value = value.replace('£', '')
                adapter[price_key] = float(value)

        # no_of_reviews(str) --> int
        reviews_key = 'no_of_reviews'
        value = adapter.get(reviews_key)
        if value:
            adapter[reviews_key] = int(value)

        # change stars into equivalent int
        stars_key = 'stars'
        star_ratings = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        value = adapter.get(stars_key, "").lower()
        adapter[stars_key] = star_ratings.get(value, 0)

        return item


class SaveToMySQLPipeline:

    def __init__(self) -> None:
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

            # Create a cursor, used to execute commands
            self.cur = self.conn.cursor()
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    url VARCHAR(255),
                    upc VARCHAR(64) UNIQUE,
                    name VARCHAR(128),
                    price_excl_tax DECIMAL(10, 2),
                    price_incl_tax DECIMAL(10, 2),
                    tax DECIMAL(10, 2),
                    price DECIMAL(10, 2),
                    type VARCHAR(32),
                    genre VARCHAR(32),
                    availability INTEGER,
                    no_of_reviews INTEGER,
                    stars INTEGER,
                    description TEXT,
                    PRIMARY KEY(id)
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def process_item(self, item, spider):
        try:
            self.cur.execute("""
            INSERT INTO books (
                url, name, price_excl_tax, price_incl_tax, tax, price,
                type, genre, availability, no_of_reviews, stars, description
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """,
        (
            item["url"],
            item["name"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["price"],
            item["type"],
            item["genre"],
            item["availability"],
            item["no_of_reviews"],
            item["stars"],
            str(item["description"])
        ))
            self.conn.commit()
        except Exception as e:
            print(f"Problem occured: {e}")
            # print(item)
        # returning item is important in process_item method in pipeline
        return item

    def close_spider(self, spider):
        # Close cursor and connection to the database.
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
