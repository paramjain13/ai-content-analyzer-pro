from scraper import scrape_website
from summarizer import summarize_text
from form_filler import fill_form

url = input("Enter website URL: ")

title, content = scrape_website(url)
summary = summarize_text(content)

print("\nTitle:", title)
print("\nSummary:", summary)

choice = input("\nFill form? (yes/no): ")
if choice == "yes":
    fill_form(url)


