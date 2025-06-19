from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

DISCLAIMER_TEXT = """
<h2>⚖️ Legal Disclaimer</h2>
<p><strong>This tool is for informational purposes only.</strong><br>
Please verify all legal case information independently. This is not a substitute for legal advice.</p>
<form action="/search" method="post">
  <button type="submit">I Understand & Continue</button>
</form>
"""

@app.route('/', methods=['GET'])
def home():
    return DISCLAIMER_TEXT

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'GET':
        return '''
        <h2>🔍 Legal Research AI</h2>
        <form action="/search" method="post">
            <input name="q" placeholder="Enter case name or citation" size="50"/>
            <button type="submit">Search</button>
        </form>
        <form action="/donate" method="get">
            <button type="submit">💖 Donate</button>
        </form>
        '''
    query = request.form['q']
    results = []

    # Arizona Courts (simulated HTML structure)
    az_url = f"https://www.azcourts.gov/search?query={requests.utils.quote(query)}"
    r = requests.get(az_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for item in soup.select('.case-result'):
        title = item.select_one('.case-title').get_text(strip=True)
        link = item.select_one('a')['href']
        full_link = requests.compat.urljoin("https://www.azcourts.gov", link)
        results.append({'source': 'Arizona Courts', 'title': title, 'link': full_link})

    # Google Scholar
    gs_url = f"https://scholar.google.com/scholar?q={requests.utils.quote(query)}"
    gs = requests.get(gs_url, headers={"User-Agent": "Mozilla/5.0"})
    gs_soup = BeautifulSoup(gs.text, 'html.parser')
    for div in gs_soup.select('.gs_ri'):
        title_tag = div.select_one('.gs_rt a')
        if not title_tag:
            continue
        title = title_tag.text
        link = title_tag['href']
        snippet = div.select_one('.gs_rs').text
        overturned = "overturn" in snippet.lower() or "reversed" in snippet.lower()
        results.append({
            'source': 'Google Scholar',
            'title': title,
            'link': link,
            'snippet': snippet,
            'overturned': overturned
        })

    # Results
    html = f'<h2>Results for: <em>{query}</em></h2><ul>'
    for r in results:
        html += f'<li><strong>[{r["source"]}]</strong> <a href="{r["link"]}" target="_blank">{r["title"]}</a>'
        if r.get('overturned'):
            html += ' ⚠️ <em>May be overturned or reversed</em>'
        html += '</li>'
    html += '</ul>'
    html += '<form action="/donate" method="get"><button type="submit">💖 Donate</button></form>'
    return html

@app.route('/donate')
def donate():
    return '''
    <h2>Support Development</h2>
    <p>If this tool helped you, please consider supporting us:</p>
    <form action="https://www.paypal.com/donate" method="post" target="_blank">
        <input type="hidden" name="hosted_button_id" value="YOUR_PAYPAL_BUTTON_ID" />
        <button type="submit">Donate via PayPal</button>
    </form>
    <form action="/" method="get">
        <button type="submit">← Back to Home</button>
    </form>
    '''

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
