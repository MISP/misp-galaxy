import re

def extract_links(text):
    links = re.findall(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', text)
    urls = set([url for text, url in links])
    return urls