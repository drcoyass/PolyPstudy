import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import os
import random
import re

print("==========================================")
print("  PolyP-Study: Ultimate Global Map Engine")
print("==========================================\n")
print("Extracting affiliations for the Elite 1000 PolyP papers...")

latest_papers_file = 'data/latest_papers.json'
output_file = 'data/institutions.json'

if not os.path.exists(latest_papers_file):
    print(f"Error: {latest_papers_file} not found.")
    exit(1)

with open(latest_papers_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    papers = data.get('papers', [])

# Take the top 1000 papers to ensure comprehensive global coverage
papers = papers[:1000]
pmids = [p['id'] for p in papers if p.get('source') == 'PubMed']
print(f"Found {len(pmids)} PMIDs for batch affiliation mapping.")

if not pmids:
    print("No valid PMIDs to process. Exiting.")
    exit(0)

raw_institutions = {} # pmid -> raw affiliation text

print('Fetching XML from PubMed in batches...')
batch_size = 200
for i in range(0, len(pmids), batch_size):
    batch = pmids[i:i+batch_size]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(batch)}&retmode=xml"
    try:
        req = urllib.request.urlopen(url)
        xml_data = req.read()
        root = ET.fromstring(xml_data)
        
        for article in root.findall('.//PubmedArticle'):
            pmid_node = article.find('.//PMID')
            if pmid_node is None: continue
            pmid = pmid_node.text
            affils = article.findall('.//Affiliation')
            if affils and affils[0].text:
                raw_institutions[pmid] = affils[0].text
        print(f"  ... Batch {i//batch_size + 1}/{(len(pmids)-1)//batch_size + 1} completed.")
        time.sleep(1)
    except Exception as e:
        print(f"Error fetching batch: {e}. Skipping to next...")

print(f"\nExtracted raw affiliations for {len(raw_institutions)} papers.")

# Group papers by cleaned institution names
print("Clustering affiliations and grouping papers by institution...")
institution_clusters = {} # clean_name -> {"raw": original, "pmids": []}

def clean_affiliation(text):
    # Extract the main university/hospital/institute name
    parts = [p.strip() for p in text.split(',')]
    for p in parts:
        lower_p = p.lower()
        if any(keyword in lower_p for keyword in ["university", "institute", "hospital", "college", "school", "center", "clinic", "corp", "ltd", "inc", "大学", "研究所", "病院", "センター"]):
            # Remove department names usually before the university if it's too long
            return p
    return parts[0] if parts else text

for pmid, affil in raw_institutions.items():
    clean_name = clean_affiliation(affil)
    # Basic normalization to merge slight variations
    norm_name = re.sub(r'[^a-zA-Z0-9]', '', clean_name.lower())
    
    found_key = None
    for existing_norm, existing_data in institution_clusters.items():
        if norm_name in existing_norm or existing_norm in norm_name:
            found_key = existing_norm
            break
            
    if found_key:
        institution_clusters[found_key]["pmids"].append(pmid)
    else:
        institution_clusters[norm_name] = {"display_name": clean_name, "raw": affil, "pmids": [pmid]}

print(f"Grouped into {len(institution_clusters)} unique research hubs.")

# Geocode unique hubs
print("\nGeocoding unique hubs (this may take a few moments)...")

map_data = []

def simple_geocode(text):
    text_lower = text.lower()
    known_locations = [
        {"keys": ["tokyo", "japan"], "lat": 35.6895, "lng": 139.6917},
        {"keys": ["osaka", "japan"], "lat": 34.6937, "lng": 135.5023},
        {"keys": ["hokkaido", "sapporo", "japan"], "lat": 43.0618, "lng": 141.3545},
        {"keys": ["stanford", "california", "usa"], "lat": 37.4275, "lng": -122.1697},
        {"keys": ["bethesda", "nih", "maryland"], "lat": 38.9996, "lng": -77.1023},
        {"keys": ["michigan", "ann arbor", "usa"], "lat": 42.2780, "lng": -83.7382},
        {"keys": ["seattle", "washington", "usa"], "lat": 47.6062, "lng": -122.3321},
        {"keys": ["new york", "usa"], "lat": 40.7128, "lng": -74.0060},
        {"keys": ["boston", "harvard", "usa"], "lat": 42.3601, "lng": -71.0589},
        {"keys": ["bonn", "germany"], "lat": 50.7374, "lng": 7.0982},
        {"keys": ["berlin", "germany"], "lat": 52.5200, "lng": 13.4050},
        {"keys": ["london", "uk", "united kingdom"], "lat": 51.5074, "lng": -0.1278},
        {"keys": ["seoul", "korea"], "lat": 37.5665, "lng": 126.9780},
        {"keys": ["beijing", "china"], "lat": 39.9042, "lng": 116.4074},
        {"keys": ["shanghai", "china"], "lat": 31.2304, "lng": 121.4737},
        {"keys": ["sydney", "australia"], "lat": -33.8688, "lng": 151.2093},
        {"keys": ["toronto", "canada"], "lat": 43.6510, "lng": -79.3470},
        {"keys": ["paris", "france"], "lat": 48.8566, "lng": 2.3522},
        {"keys": ["kyoto", "japan"], "lat": 35.0116, "lng": 135.7681},
        {"keys": ["fukuoka", "japan", "kyushu"], "lat": 33.5902, "lng": 130.4017},
        {"keys": ["switzerland", "zurich", "geneva"], "lat": 46.8182, "lng": 8.2275},
        {"keys": ["spain", "madrid", "barcelona"], "lat": 40.4637, "lng": -3.7492},
        {"keys": ["italy", "rome", "milan"], "lat": 41.8719, "lng": 12.5674},
    ]
    
    for loc in known_locations:
        if any(k in text_lower for k in loc["keys"]):
            return loc["lat"] + random.uniform(-0.6, 0.6), loc["lng"] + random.uniform(-0.6, 0.6)
            
    try:
        # Nominatim lookup for everything else
        query = text.split(',')[0].strip()
        safe_query = urllib.parse.quote(query)
        geo_url = f"https://nominatim.openstreetmap.org/search?q={safe_query}&format=json&limit=1"
        req = urllib.request.Request(geo_url, headers={'User-Agent': 'PolyPstudy/2.0'})
        res = urllib.request.urlopen(req)
        geo_res = json.loads(res.read())
        if geo_res and len(geo_res) > 0:
            return float(geo_res[0]['lat']), float(geo_res[0]['lon'])
    except:
        pass
        
    return None

success_count = 0
for norm_key, data in list(institution_clusters.items()):
    coords = simple_geocode(data["raw"])
    if coords:
        # We successfully geocoded
        map_data.append({
            "name": data["display_name"],
            "raw_affiliation": data["raw"],
            "paperCount": len(data["pmids"]),
            "pmids": data["pmids"],
            "lat": coords[0],
            "lng": coords[1]
        })
        success_count += 1
    time.sleep(0.5) # respectful delay

# Deduplicate essentially identical coords to prevent complete overlaps
for m in map_data:
    for n in map_data:
        if m != n and abs(m['lat']-n['lat']) < 0.001 and abs(m['lng']-n['lng']) < 0.001:
            m['lat'] += random.uniform(-0.05, 0.05)
            m['lng'] += random.uniform(-0.05, 0.05)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({"updated_at": time.strftime("%Y-%m-%d"), "locations": map_data}, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully generated {output_file} featuring {success_count} globally plotted institutions!")
print(f"Total papers actively linked on the map: {sum(len(d['pmids']) for d in map_data)}")
print("When you push this to main, clicking a map point will now filter the library for that institution's papers!")
