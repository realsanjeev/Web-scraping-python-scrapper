'''Project uses scrappy to scrape the website and display it to user'''
from flask import Flask, render_template, request
from jinja2 import Environment, PackageLoader
from pipeline import (
    MyDatabase, 
    DB_HOST, 
    DB_USER, 
    DB_PASSWORD, 
    DB_NAME
)


app = Flask(__name__)

# Create a Jinja2 environment
env = Environment(loader=PackageLoader("app"))

# Define the custom 'enumerate' filter
def enumerate_filter(iterable, start=0):
    '''Custom filter'''
    return zip(range(start, len(iterable) + start), iterable)

env.filters['enumerate'] = enumerate_filter

# constant variable
LIMIT=10

@app.route('/')
def index():
    '''Home page view'''
    return render_template('index.html')

@app.route('/book')
def book_view():
    '''Book view from bookscrape'''
    page = request.args.get("page", 1, type=int) 
    offset = 0 if page<=1 else (page-1) * LIMIT

    try:
        with MyDatabase(db_host=DB_HOST, db_user=DB_USER, db_password=DB_PASSWORD, db_name=DB_NAME) as database:
            tables = database.get_tables_name()
            if not tables:
                return render_template('book.html', columns=[], records=[], error="No tables found. Please run the scraper.")
            
            # Assuming the first table is the one we want, or specific logic
            # For now, let's look for 'books' or take the first one
            target_table = 'books' if 'books' in tables else tables[0]
            
            columns = database.get_column_names(table_name=target_table)
            records = database.get_records(table=target_table, limit=LIMIT, offset=offset)
            
            return render_template('book.html', columns=columns, records=records)
    except Exception as e:
        return render_template('book.html', columns=[], records=[], error=f"Database error: {e}")

@app.route('/quotes')
def quotes_view():
    '''Display quotes from scraping the quotes stored in db'''
    try:
        # Both scrapers now use the same database
        with MyDatabase(db_host=DB_HOST, db_user=DB_USER, db_password=DB_PASSWORD, db_name=DB_NAME) as database:
            # Custom query to join quotes and authors
            query = """
                SELECT q.quote, a.name as author, q.tags 
                FROM quotes q 
                JOIN authors a ON q.author_id = a.id
            """
            try:
                database.cur.execute(query)
                records = database.cur.fetchall()
                columns = ["Quote", "Author", "Tags"]
                return render_template('quotes.html', columns=columns, records=records)
            except Exception as e:
                 # Fallback or error if tables don't exist yet
                 return render_template('quotes.html', columns=[], records=[], error=f"Database error (tables might be missing): {e}")
    except Exception as e:
        return render_template('quotes.html', columns=[], records=[], error=f"Database error: {e}")

@app.route('/contacts')
def contacts_view():
    '''Contact us view'''
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
