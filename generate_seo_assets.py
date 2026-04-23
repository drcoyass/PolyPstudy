import json
import os
from datetime import datetime

def generate_seo_assets():
    print("Generating SEO Assets (Sitemap & Robots)...")
    
    # 1. Load data to get paper count and categories
    data_path = 'data/latest_papers.json'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    last_mod = datetime.now().strftime("%Y-%m-%d")
    base_url = "https://poly-pstudy.vercel.app/"

    # 2. Generate Sitemap.xml
    # We include the main page and high-level sections for crawling
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}</loc>
        <lastmod>{last_mod}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""

    with open('public/sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)

    # 3. Generate Robots.txt
    robots = f"""User-agent: *
Allow: /
Sitemap: {base_url}sitemap.xml
"""
    with open('public/robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots)
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots)

    print(f"Success! Sitemap and Robots.txt generated for {len(papers)} research records.")

if __name__ == "__main__":
    generate_seo_assets()
