import json
import urllib.request
import xml.etree.ElementTree as ET
import time
import os

print("Starting Affiliation Extraction...")

with open('data/latest_papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    papers = data.get('papers', [])

# Take the top 100 Elite papers for generating the global map
# To make it truly representative of the "World Map", we select the top 300 recent/elite papers
papers = papers[:300]
pmids = [p['id'] for p in papers if p.get('source') == 'PubMed']
print(f"Found {len(pmids)} PMIDs for affiliation mapping.")

institutions = {} # dict of id -> list of affiliations

# Fetch in batches of 100
for i in range(0, len(pmids), 100):
    batch = pmids[i:i+100]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(batch)}&retmode=xml"
    
    try:
        req = urllib.request.urlopen(url)
        xml_data = req.read()
        root = ET.fromstring(xml_data)
        
        for article in root.findall('.//PubmedArticle'):
            pmid = article.find('.//PMID').text
            affils = article.findall('.//Affiliation')
            if affils:
                # Just take the first affiliation for simplicity
                institutions[pmid] = affils[0].text
        
        print(f"Processed batch {i//100 + 1}")
        time.sleep(1) # rate limit
    except Exception as e:
        print(f"Error fetching batch: {e}")

print(f"Extracted affiliations for {len(institutions)} papers.")

# Now, we do some basic NLP / keyword extraction to map to known countries/cities or use a basic dictionary.
# Since we can't reliably geocode 300 strings without an API key (Nominatim will rate limit severely),
# we will construct a beautiful mock/heuristic geocoder for major regions based on keywords.

geo_db = [
    {"keywords": ["Japan", "Tokyo", "Osaka", "Hokkaido", "Kyoto"], "lat": 36.2048, "lng": 138.2529, "country": "Japan"},
    {"keywords": ["USA", "United States", "New York", "California", "Boston", "NIH"], "lat": 37.0902, "lng": -95.7129, "country": "USA"},
    {"keywords": ["Germany", "Bonn", "Berlin", "Munich"], "lat": 51.1657, "lng": 10.4515, "country": "Germany"},
    {"keywords": ["China", "Beijing", "Shanghai", "Guangzhou"], "lat": 35.8617, "lng": 104.1954, "country": "China"},
    {"keywords": ["UK", "London", "Oxford", "Cambridge", "United Kingdom"], "lat": 55.3781, "lng": -3.4360, "country": "UK"},
    {"keywords": ["Korea", "Seoul"], "lat": 35.9078, "lng": 127.7669, "country": "South Korea"},
    {"keywords": ["France", "Paris"], "lat": 46.2276, "lng": 2.2137, "country": "France"},
    {"keywords": ["Italy", "Rome", "Milan"], "lat": 41.8719, "lng": 12.5674, "country": "Italy"},
    {"keywords": ["Canada", "Toronto", "Vancouver"], "lat": 56.1304, "lng": -106.3468, "country": "Canada"},
    {"keywords": ["Australia", "Sydney", "Melbourne"], "lat": -25.2744, "lng": 133.7751, "country": "Australia"},
]

map_data = []

# We'll also extract actual institution names for display
for pmid, affil_text in institutions.items():
    country = "Unknown"
    lat, lng = 0, 0
    display_name = affil_text.split(',')[0] if ',' in affil_text else affil_text
    if len(display_name) > 60: display_name = display_name[:60] + "..."
    
    for geo in geo_db:
        if any(kw.lower() in affil_text.lower() for kw in geo['keywords']):
            country = geo['country']
            # add a slight random offset so markers don't perfectly overlap
            import random
            lat = geo['lat'] + (random.uniform(-2, 2))
            lng = geo['lng'] + (random.uniform(-3, 3))
            break
            
    if country != "Unknown":
        map_data.append({
            "pmid": pmid,
            "affiliation": display_name,
            "country": country,
            "lat": lat,
            "lng": lng
        })

print(f"Mapped {len(map_data)} valid locations.")
with open('data/map_institutions.json', 'w', encoding='utf-8') as f:
    json.dump(map_data, f, ensure_ascii=False, indent=2)
    
print("Map data saved to data/map_institutions.json")
