import re
from bs4 import BeautifulSoup


def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
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
links = extract_links_from_html(html_content)

# for link in links:
#     print(link)

# print(f"Count of links: {len(links)}")

news_ids = []
for link in links:
    last_part = link.split("/")[-1]
    if re.match(r"^\d{8}$", last_part):
        news_ids.append(int(last_part))

# Print the eight digit numbers
# for number in news_ids:
#     print(number)

print(news_ids)
