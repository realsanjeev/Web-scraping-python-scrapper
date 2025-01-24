# Web Scraping Python Scraper

This project demonstrates a web scraping pipeline using **Scrapy**, **Flask**, and **MySQL**, fully containerized with **Docker**.

It includes two main scrapers:
1.  **Book Scraper**: Scrapes books from [books.toscrape.com](http://books.toscrape.com).
2.  **Quotes Scraper**: Scrapes quotes and authors from [quotes.toscrape.com](http://quotes.toscrape.com).

## Features
- **Scrapy**: Powerful web crawling and scraping.
- **Flask**: Web interface to view scraped data.
- **MySQL**: Persistent storage for scraped data.
- **Docker**: Easy deployment and environment management.
- **Secure Configuration**: Uses `.env` for sensitive credentials.
- **Normalized Schema**: Efficient database design for quotes and authors.

## Prerequisites
- Docker and Docker Compose installed on your machine.

## Getting Started

### 1. Configuration
Create a `.env` file in the root directory to configure your database credentials. You can copy the example below:

```bash
# .env
DB_HOST=mysql
DB_USER=user
DB_PASSWORD=user_password
DB_NAME=bookdb
```

> [!NOTE]
> When running with Docker, `DB_HOST` should be set to `mysql` (the service name).

### 2. Run the Application
Start the entire stack (Database + Web App) using Docker Compose:

```bash
docker compose up --build
```

- The Flask application will be available at: [http://localhost:5000](http://localhost:5000)
- The MySQL database will be running on port `3306`.

### 3. Running Scrapers
To populate the database, you need to run the spiders. You can run them inside the running web container.

**Run Book Scraper:**
```bash
docker compose exec web bash -c "cd bookscrape && scrapy crawl bookspider"
```

**Run Quotes Scraper:**
```bash
docker compose exec web bash -c "cd quotes_scrape && scrapy crawl quotespider"
```

### 4. View Data
Once the scrapers have finished, visit [http://localhost:5000](http://localhost:5000) to browse the data:
- **Books**: [http://localhost:5000/book](http://localhost:5000/book)
- **Quotes**: [http://localhost:5000/quotes](http://localhost:5000/quotes)

## Project Structure

- `bookscrape/`: Scrapy project for books.
- `quotes_scrape/`: Scrapy project for quotes (with normalized schema).
- `app.py`: Flask application for the web interface.
- `pipeline.py`: Database connection logic (refactored to use `.env`).
- `docker-compose.yaml`: Docker services configuration.
- `Dockerfile`: Build instructions for the web app.

## Troubleshooting

### Database Permission Errors
If you encounter database permission errors like `Access denied for user 'user'@'%' to database 'scraper_db'`, it's likely because the MySQL volume contains old database data. To fix this:

```bash
# Stop containers and remove volumes
docker compose down -v

# Start fresh
docker compose up -d
```

> [!WARNING]
> Using `-v` will delete all scraped data. Make sure to backup if needed.

## Development

If you want to run the project locally without Docker (not recommended for beginners due to database setup):

1.  Install dependencies: `pip install -r requirements.txt`
2.  Set up a local MySQL database.
3.  Update `.env` with `DB_HOST=localhost`.
4.  Run the app: `python app.py`

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the [GNU GENERAL PUBLIC LICENSE](LICENSE).
