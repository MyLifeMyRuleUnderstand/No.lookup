from flask import Flask, request, Response, render_template_string
import requests

app = Flask(__name__)

# ---------- HTML (वही search interface) ----------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Phone Number Lookup</title>
    <style>
        /* (पूरा CSS – आपने जो दिया था, वही copy करें) */
        *,
        *::before,
        *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Roboto, system-ui, -apple-system, sans-serif;
            background: #f0f4f8;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 2rem 1rem;
        }
        .container {
            max-width: 820px;
            width: 100%;
            background: #ffffff;
            border-radius: 28px;
            box-shadow: 0 20px 60px rgba(0, 20, 40, 0.10);
            padding: 2rem 2rem 2.5rem;
        }
        .app-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .app-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #0b1e33;
        }
        .app-header h1 span {
            color: #2563eb;
        }
        .app-header p {
            color: #5f6c80;
            font-size: 0.95rem;
            margin-top: 0.3rem;
        }
        .search-box {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 1.8rem;
        }
        .search-box input {
            flex: 1 1 220px;
            padding: 0.85rem 1.2rem;
            font-size: 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            outline: none;
            transition: 0.25s;
            background: #fafcff;
            color: #0b1e33;
        }
        .search-box input:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
        }
        .search-box input::placeholder {
            color: #94a3b8;
        }
        .search-box button {
            padding: 0.85rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            background: #2563eb;
            color: #fff;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            transition: 0.2s;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            white-space: nowrap;
        }
        .search-box button:hover {
            background: #1d4ed8;
            transform: scale(1.02);
        }
        .search-box button:active {
            transform: scale(0.97);
        }
        .search-box button:disabled {
            opacity: 0.6;
            pointer-events: none;
        }
        .status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: #334155;
            padding: 0.25rem 0 0.75rem;
            border-bottom: 1px solid #eef2f6;
            margin-bottom: 1.5rem;
        }
        .status .count {
            font-weight: 600;
            background: #eef2ff;
            padding: 0.2rem 0.9rem;
            border-radius: 40px;
            color: #2563eb;
            font-size: 0.85rem;
        }
        .status .queried-number {
            font-family: 'SF Mono', 'Fira Code', monospace;
            background: #f1f5f9;
            padding: 0.2rem 0.9rem;
            border-radius: 40px;
            font-size: 0.85rem;
            color: #0b1e33;
        }
        .results {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }
        .result-card {
            background: #fafcff;
            border-radius: 20px;
            border: 1px solid #e9edf3;
            padding: 1.25rem 1.5rem;
            transition: 0.2s;
        }
        .result-card:hover {
            border-color: #cbd5e1;
        }
        .result-card .kv-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 0.5rem 1.2rem;
            align-items: baseline;
        }
        .result-card .kv-key {
            font-weight: 600;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            color: #475569;
            padding: 0.3rem 0;
            border-bottom: 1px dashed #e9edf3;
        }
        .result-card .kv-value {
            font-size: 0.95rem;
            color: #0b1e33;
            padding: 0.3rem 0;
            border-bottom: 1px dashed #e9edf3;
            word-break: break-word;
        }
        .result-card .kv-value .empty {
            color: #94a3b8;
            font-style: italic;
        }
        .result-card .kv-key:last-child,
        .result-card .kv-value:last-child {
            border-bottom: none;
        }
        .empty-state {
            text-align: center;
            padding: 3rem 1rem 2rem;
            color: #64748b;
        }
        .empty-state .icon {
            font-size: 3rem;
            margin-bottom: 0.8rem;
            opacity: 0.5;
        }
        .empty-state h3 {
            font-weight: 500;
            font-size: 1.1rem;
            color: #1e293b;
        }
        .empty-state p {
            font-size: 0.9rem;
            margin-top: 0.3rem;
        }
        .error-state {
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 16px;
            padding: 1.2rem 1.5rem;
            color: #b91c1c;
            text-align: center;
        }
        .loader {
            display: none;
            justify-content: center;
            padding: 2rem 0 1.5rem;
        }
        .loader.active {
            display: flex;
        }
        .loader .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 0.75s linear infinite;
        }
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
        @media (max-width: 600px) {
            .container {
                padding: 1.25rem;
            }
            .app-header h1 {
                font-size: 1.5rem;
            }
            .search-box input {
                flex: 1 1 100%;
            }
            .search-box button {
                width: 100%;
                justify-content: center;
            }
            .result-card .kv-grid {
                grid-template-columns: 1fr;
                gap: 0.2rem;
            }
            .result-card .kv-key {
                border-bottom: none;
                padding-bottom: 0;
                font-size: 0.75rem;
                color: #64748b;
            }
            .result-card .kv-value {
                padding-top: 0;
                padding-bottom: 0.6rem;
                border-bottom: 1px solid #eef2f6;
            }
            .result-card .kv-value:last-child {
                border-bottom: none;
            }
            .status {
                flex-direction: column;
                align-items: stretch;
                text-align: center;
                gap: 0.3rem;
            }
        }
        @media (max-width: 400px) {
            .container {
                padding: 1rem;
            }
            .result-card {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="app-header">
            <h1>🔍 <span>Number</span>Lookup</h1>
            <p>Enter any phone number to retrieve associated details</p>
        </div>
        <div class="search-box">
            <input type="text" id="phoneInput" placeholder="e.g. 8809989479" maxlength="15" autofocus />
            <button id="searchBtn">🔎 Search</button>
        </div>
        <div class="status" id="statusBar">
            <span class="queried-number" id="queriedDisplay">—</span>
            <span class="count" id="countDisplay">0 records</span>
        </div>
        <div class="loader" id="loader">
            <div class="spinner"></div>
        </div>
        <div id="resultsContainer">
            <div class="empty-state" id="emptyState">
                <div class="icon">📇</div>
                <h3>No results yet</h3>
                <p>Search a phone number to see details here</p>
            </div>
        </div>
    </div>

    <script>
        (function() {
            const phoneInput = document.getElementById('phoneInput');
            const searchBtn = document.getElementById('searchBtn');
            const queriedDisplay = document.getElementById('queriedDisplay');
            const countDisplay = document.getElementById('countDisplay');
            const loader = document.getElementById('loader');
            const resultsContainer = document.getElementById('resultsContainer');

            function sanitizeNumber(raw) {
                return raw.replace(/\\s+/g, '').replace(/^\\+91/, '').replace(/[^0-9]/g, '');
            }

            function formatKey(key) {
                return key.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
            }

            function safeValue(val) {
                if (val === null || val === undefined || val === '') {
                    return '<span class="empty">—</span>';
                }
                return val;
            }

            function extractJSON(text) {
                const firstBrace = text.indexOf('{');
                const lastBrace = text.lastIndexOf('}');
                if (firstBrace === -1 || lastBrace === -1 || lastBrace < firstBrace) {
                    throw new Error('No valid JSON object found');
                }
                return JSON.parse(text.substring(firstBrace, lastBrace + 1));
            }

            function renderResults(data) {
                resultsContainer.innerHTML = '';
                loader.classList.remove('active');
                if (!data || !data.success || !data.results || data.results.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="empty-state">
                            <div class="icon">🔎</div>
                            <h3>No information found</h3>
                            <p>Try a different phone number</p>
                        </div>
                    `;
                    countDisplay.textContent = '0 records';
                    queriedDisplay.textContent = data?.number ? `+91${data.number}` : '—';
                    return;
                }
                const number = data.number || '—';
                const total = data.total || data.results.length;
                queriedDisplay.textContent = `+91${number}`;
                countDisplay.textContent = `${total} record${total > 1 ? 's' : ''}`;
                let html = '<div class="results">';
                data.results.forEach(item => {
                    const fields = ['mobile', 'name', 'father_name', 'address', 'alternate', 'circle', 'aadhar', 'email'];
                    html += `<div class="result-card"><div class="kv-grid">`;
                    fields.forEach(key => {
                        const val = item[key] !== undefined ? item[key] : null;
                        html += `
                            <div class="kv-key">${formatKey(key)}</div>
                            <div class="kv-value">${safeValue(val)}</div>
                        `;
                    });
                    html += `</div></div>`;
                });
                html += '</div>';
                resultsContainer.innerHTML = html;
            }

            async function searchNumber(rawNumber) {
                const cleaned = sanitizeNumber(rawNumber);
                if (!cleaned) {
                    alert('Please enter a valid phone number.');
                    return;
                }
                searchBtn.disabled = true;
                searchBtn.textContent = '⏳ Searching...';
                loader.classList.add('active');
                resultsContainer.innerHTML = '';
                queriedDisplay.textContent = `+91${cleaned}`;
                countDisplay.textContent = '…';

                try {
                    // अब proxy का use – same origin, relative URL
                    const url = `/api/search/${cleaned}`;
                    const response = await fetch(url, {
                        method: 'GET',
                        headers: { 'Accept': 'application/json' }
                    });
                    if (!response.ok) {
                        throw new Error(`Server responded with ${response.status}`);
                    }
                    const rawText = await response.text();
                    const data = extractJSON(rawText);
                    renderResults(data);
                } catch (err) {
                    console.error('Search error:', err);
                    loader.classList.remove('active');
                    resultsContainer.innerHTML = `
                        <div class="error-state">
                            ⚠️ Failed to fetch data. Please check your connection or try again later.
                            <br><small style="color:#7f1d1d;">${err.message}</small>
                        </div>
                    `;
                    countDisplay.textContent = 'error';
                } finally {
                    searchBtn.disabled = false;
                    searchBtn.textContent = '🔎 Search';
                    loader.classList.remove('active');
                }
            }

            searchBtn.addEventListener('click', () => searchNumber(phoneInput.value));
            phoneInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    searchNumber(phoneInput.value);
                }
            });
            phoneInput.focus();

            // auto-search from URL param ?q=number
            const params = new URLSearchParams(window.location.search);
            const queryNumber = params.get('q');
            if (queryNumber) {
                phoneInput.value = queryNumber;
                searchNumber(queryNumber);
            }
        })();
    </script>
</body>
</html>
"""

# ---------- Proxy Route (सारे /api/* request को forward करेगा) ----------
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Target external API
    target_base = "https://lynx.mireiariosss.workers.dev"
    target_url = f"{target_base}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"

    # Headers copy – Referer को हटाएँ
    headers = {k: v for k, v in request.headers if k.lower() != 'referer'}

    # Forward request
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        data=request.get_data(),
        allow_redirects=False,
    )

    # CORS headers add करें
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response_headers = [(k, v) for k, v in resp.raw.headers.items()
                        if k.lower() not in excluded_headers]
    response_headers.append(('Access-Control-Allow-Origin', '*'))
    response_headers.append(('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'))
    response_headers.append(('Access-Control-Allow-Headers', 'Content-Type, Accept'))

    return Response(resp.content, resp.status_code, response_headers)

# ---------- Serve HTML at root ----------
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

# OPTIONS request के लिए (CORS preflight)
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_proxy(path):
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
