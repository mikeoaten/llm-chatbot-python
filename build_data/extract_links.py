"""
This module contains a function to extract specific links from
HTML content. 

The function `extract_links_from_html` takes a string of HTML 
content as input, parses it using BeautifulSoup, and returns a
list of links that start with "https://www.londonstockexchange.com/news-article/LLOY/".

The module then reads an HTML file, uses the function to extract
links from the file's content, and stores these links in `captured_links`.

Next, it iterates over each link in `captured_links`, splits the
link to get the last part, and checks if this last part is an eight-digit
number. If it is, the number is added to the `news_ids` list.

Finally, the module prints the `news_ids` list, which contains the
eight-digit numbers extracted from the links.
"""

import re
from bs4 import BeautifulSoup


def extract_links_from_html(input_html_content):
    """
    Extracts links from HTML content that start with
    "https://www.londonstockexchange.com/news-article/LLOY/".

    Args:
        input_html_content (str): The HTML content to extract links from.

    Returns:
        list: A list of links that match the specified criteria.
    """
    soup = BeautifulSoup(input_html_content, "html.parser")
    links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith(
            "https://www.londonstockexchange.com/news-article/LLOY/"
        )
    ]
    return links


# Read the HTML file
with open("auxilary/news_download.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Use the function
captured_links = extract_links_from_html(html_content)

# for link in links:
#     print(link)

# print(f"Count of links: {len(links)}")

news_ids = []
for link in captured_links:
    last_part = link.split("/")[-1]
    if re.match(r"^\d{8}$", last_part):
        news_ids.append(int(last_part))

# Print the eight digit numbers
# for number in news_ids:
#     print(number)

print(news_ids)
