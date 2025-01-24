# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from itemadapter import ItemAdapter
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "scraper_db") # Default to scraper_db if not set

class QuotesScrapePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item=item)

        ## strip all trailing and leading whitespaces from strings in value if any
        field_names = ["author", "quote"]

        for field_name in field_names:
            value = adapter.get(field_name)
            if value:
                adapter[field_name] = value.strip()
        
        # lowercase tags
        field_tags = "tags"
        tags = adapter.get(field_tags)
        if tags:
            adapter[field_tags] = [tag.lower().strip() for tag in tags]

        # cleaning author_data
        author_field = "author_info"
        author_data = adapter.get(author_field)
        if author_data:
            for (key, values) in author_data.items():
                if author_data[key]:
                    author_data[key] = author_data[key].strip().replace("\"", "'")
            adapter[author_field] = author_data
        return item


class SaveQuotesItemMySQL:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            self.cur = self.conn.cursor()
            
            # Create authors table first (parent)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER NOT NULL AUTO_INCREMENT,
                name VARCHAR(128) UNIQUE,
                dob DATE,
                birthplace VARCHAR(255),
                description TEXT,
                PRIMARY KEY (id)
            )
            """)
            
            # Create quotes table (child)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER NOT NULL AUTO_INCREMENT,
                quote TEXT,
                tags VARCHAR(255),
                author_id INTEGER,
                PRIMARY KEY (id),
                FOREIGN KEY (author_id) REFERENCES authors(id)
            )
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def process_item(self, item, spider):
        author_item = item.get("author_info")
        if not author_item:
            return item

        try:
            # Parse the date and format it to 'YYYY-MM-DD'
            dob_formatted = None
            if author_item.get("dob"):
                try:
                    dob_formatted = datetime.strptime(author_item["dob"], '%B %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    pass # Handle date parsing error if needed

            # Check if author exists
            self.cur.execute("SELECT id FROM authors WHERE name = %s", (author_item["name"],))
            result = self.cur.fetchone()

            if result:
                author_id = result[0]
            else:
                # Insert new author
                self.cur.execute("""
                    INSERT INTO authors (name, dob, birthplace, description)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (author_item["name"],
                    dob_formatted,
                    author_item["birth_place"],
                    author_item["description"])
                )
                author_id = self.cur.lastrowid
            
            # Insert quote linked to author
            tags_str = ','.join(item["tags"]) if item.get("tags") else ""
            
            self.cur.execute("""
                INSERT INTO quotes (quote, tags, author_id) VALUES (%s, %s, %s)
                """,
                (item["quote"],
                tags_str,
                author_id)
            )

            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error processing item: {err}")
            self.conn.rollback()
            
        return item
    
    def close_spider(self, spider):
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
