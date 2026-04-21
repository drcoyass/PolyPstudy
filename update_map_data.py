import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import os
import random

print("==========================================")
print("  PolyP-Study: Global Map Data Generator")
print("==========================================\n")
print("Extracting actual affiliations from PubMed...")

latest_papers_file = 'data/latest_papers.json'
output_file = 'data/institutions.json'

if not os.path.exists(latest_papers_file):
    print(f"Error: {latest_papers_file} not found.")
    exit(1)

with open(latest_papers_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    papers = data.get('papers', [])

# Take the top 50 Elite/Recent papers for the map so we don't spam PubMed
papers = papers[:50]
pmids = [p['id'] for p in papers if p.get('source') == 'PubMed']
print(f"Found {len(pmids)} PMIDs for affiliation mapping.")

if not pmids:
    print("No valid PMIDs to process. Exiting.")
    exit(0)

url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=xml"

institutions = {}
try:
    print('Fetching XML from PubMed...')
    req = urllib.request.urlopen(url)
    xml_data = req.read()
    root = ET.fromstring(xml_data)
    
    for article in root.findall('.//PubmedArticle'):
        pmid = article.find('.//PMID').text
        affils = article.findall('.//Affiliation')
        if affils:
            institutions[pmid] = affils[0].text
    
    print(f"Extracted affiliations for {len(institutions)} papers.")
except Exception as e:
    print(f"Error fetching data: {e}. Are you connected to the internet?")
    exit(1)

print("\nGeocoding affiliations (this may take a few seconds due to API limits)...")

map_data = []

def simple_geocode(text):
    text_lower = text.lower()
    
    # Simple hardcoded fallback mapping for high reliability without API keys
    known_locations = [
        {"keys": ["tokyo", "japan"], "lat": 35.6895, "lng": 139.6917},
        {"keys": ["osaka", "japan"], "lat": 34.6937, "lng": 135.5023},
        {"keys": ["hokkaido", "japan", "sapporo"], "lat": 43.0618, "lng": 141.3545},
        {"keys": ["stanford", "california", "usa"], "lat": 37.4275, "lng": -122.1697},
        {"keys": ["bethesda", "nih", "maryland"], "lat": 38.9996, "lng": -77.1023},
        {"keys": ["michigan", "ann arbor"], "lat": 42.2780, "lng": -83.7382},
        {"keys": ["new york", "usa"], "lat": 40.7128, "lng": -74.0060},
        {"keys": ["bonn", "germany"], "lat": 50.7374, "lng": 7.0982},
        {"keys": ["berlin", "germany"], "lat": 52.5200, "lng": 13.4050},
        {"keys": ["london", "uk", "united kingdom"], "lat": 51.5074, "lng": -0.1278},
        {"keys": ["seoul", "korea"], "lat": 37.5665, "lng": 126.9780},
        {"keys": ["beijing", "china"], "lat": 39.9042, "lng": 116.4074},
        {"keys": ["shanghai", "china"], "lat": 31.2304, "lng": 121.4737},
        {"keys": ["sydney", "australia"], "lat": -33.8688, "lng": 151.2093},
        {"keys": ["toronto", "canada"], "lat": 43.6510, "lng": -79.3470},
        {"keys": ["paris", "france"], "lat": 48.8566, "lng": 2.3522},
    ]
    
    for loc in known_locations:
        if any(k in text_lower for k in loc["keys"]):
            # Add spread to avoid exact overlap on map
            return loc["lat"] + random.uniform(-0.5, 0.5), loc["lng"] + random.uniform(-0.5, 0.5)
            
    # Try Nominatim as a fallback
    try:
        # Just grab the main institution unit to increase match probability
        query = text.split(',')[0].strip()
        safe_query = urllib.parse.quote(query)
        geo_url = f"https://nominatim.openstreetmap.org/search?q={safe_query}&format=json&limit=1"
        req = urllib.request.Request(geo_url, headers={'User-Agent': 'PolyPstudy/1.0'})
        res = urllib.request.urlopen(req)
        geo_res = json.loads(res.read())
        if geo_res and len(geo_res) > 0:
            return float(geo_res[0]['lat']), float(geo_res[0]['lon'])
    except:
        pass
        
    return None

success_count = 0
for pmid, affil in institutions.items():
    coords = simple_geocode(affil)
    if coords:
        # Get brief author metadata if possible from original json
        paper_info = next((p for p in papers if p['id'] == pmid), None)
        title = paper_info['title'] if paper_info else "Polyphosphate Research"
        
        map_data.append({
            "pmid": pmid,
            "affiliation": affil,
            "title": title,
            "lat": coords[0],
            "lng": coords[1]
        })
        success_count += 1
    # Be nice to APIs
    time.sleep(0.5)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({"updated_at": time.strftime("%Y-%m-%d"), "locations": map_data}, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully generated {output_file} with {success_count} geocoded locations.")
print("The Poly-Pstudy interactive map will now load this realistic data automatically!")
