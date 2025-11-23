/**
 * Social Media Scraping Page
 * Beautiful interface for scraping social media platforms.
 */

import { useState, useContext } from 'react';
import { ThemeContext } from './_app';
import ScrapeCard from '../components/ScrapeCard';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

const PLATFORMS = [
  { value: 'twitter', label: 'Twitter/X', icon: '🐦' },
  { value: 'instagram', label: 'Instagram', icon: '📷' },
  { value: 'linkedin', label: 'LinkedIn', icon: '💼' },
  { value: 'reddit', label: 'Reddit', icon: '🤖' },
  { value: 'youtube', label: 'YouTube', icon: '📺' }
];

const SCRAPE_TYPES = [
  { value: 'profile', label: 'Profile', description: 'Scrape user profile information' },
  { value: 'posts', label: 'Posts', description: 'Scrape recent posts from a user' },
  { value: 'search', label: 'Search', description: 'Search posts by keyword/hashtag' },
  { value: 'url', label: 'URL', description: 'Scrape any URL directly' }
];

const ENGINES = [
  { value: 'beautifulsoup', label: 'BeautifulSoup', description: 'Fast, for static HTML' },
  { value: 'selenium', label: 'Selenium', description: 'Browser automation' },
  { value: 'playwright', label: 'Playwright', description: 'Modern async (recommended)' }
];

export default function ScrapePage() {
  const { theme, setTheme } = useContext(ThemeContext);
  const [scrapeType, setScrapeType] = useState('profile');
  const [platform, setPlatform] = useState('twitter');
  const [username, setUsername] = useState('');
  const [query, setQuery] = useState('');
  const [url, setUrl] = useState('');
  const [limit, setLimit] = useState(10);
  const [engine, setEngine] = useState('playwright');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  async function handleScrape(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let endpoint = '';
      let body = {};

      switch (scrapeType) {
        case 'profile':
          endpoint = '/api/scrape/profile';
          body = { platform, username };
          break;
        case 'posts':
          endpoint = '/api/scrape/posts';
          body = { platform, username, limit };
          break;
        case 'search':
          endpoint = '/api/scrape/search';
          body = { platform, query, limit };
          break;
        case 'url':
          endpoint = '/api/scrape/url';
          body = { url, engine };
          break;
        default:
          throw new Error('Invalid scrape type');
      }

      const resp = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.detail || 'Scraping failed');
      }

      setResults(data);
    } catch (err) {
      console.error('Scrape error:', err);
      setError(err.message || 'An error occurred while scraping');
    } finally {
      setLoading(false);
    }
  }

  function toggleTheme() {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  }

  return (
    <div className="scrape-page">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <a href="/" className="back-link">← Back to Chat</a>
        </div>
        <div className="scrape-types">
          <h3>Scrape Type</h3>
          {SCRAPE_TYPES.map(type => (
            <button
              key={type.value}
              className={`scrape-type-btn ${scrapeType === type.value ? 'active' : ''}`}
              onClick={() => setScrapeType(type.value)}
            >
              <span className="type-label">{type.label}</span>
              <span className="type-desc">{type.description}</span>
            </button>
          ))}
        </div>
      </aside>

      {/* Main content */}
      <main className="main scrape-main">
        <header className="header">
          <div>
            <h1 className="page-title">Social Scraper</h1>
            <span className="page-subtitle">Extract data from social media platforms</span>
          </div>
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {theme === 'dark' ? '☀️' : '🌑'}
          </button>
        </header>

        <div className="scrape-content">
          {/* Scraping Form */}
          <form className="scrape-form" onSubmit={handleScrape}>
            {scrapeType !== 'url' && (
              <div className="form-group">
                <label>Platform</label>
                <div className="platform-selector">
                  {PLATFORMS.map(p => (
                    <button
                      key={p.value}
                      type="button"
                      className={`platform-btn ${platform === p.value ? 'active' : ''}`}
                      onClick={() => setPlatform(p.value)}
                    >
                      <span className="platform-icon">{p.icon}</span>
                      <span className="platform-label">{p.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {(scrapeType === 'profile' || scrapeType === 'posts') && (
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  placeholder="Enter username (without @)"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                />
              </div>
            )}

            {scrapeType === 'search' && (
              <div className="form-group">
                <label htmlFor="query">Search Query</label>
                <input
                  id="query"
                  type="text"
                  placeholder="Enter keyword or #hashtag"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  required
                />
              </div>
            )}

            {scrapeType === 'url' && (
              <>
                <div className="form-group">
                  <label htmlFor="url">URL</label>
                  <input
                    id="url"
                    type="url"
                    placeholder="https://example.com/page"
                    value={url}
                    onChange={e => setUrl(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Scraping Engine</label>
                  <div className="engine-selector">
                    {ENGINES.map(eng => (
                      <button
                        key={eng.value}
                        type="button"
                        className={`engine-btn ${engine === eng.value ? 'active' : ''}`}
                        onClick={() => setEngine(eng.value)}
                      >
                        <span className="engine-label">{eng.label}</span>
                        <span className="engine-desc">{eng.description}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}

            {(scrapeType === 'posts' || scrapeType === 'search') && (
              <div className="form-group">
                <label htmlFor="limit">Limit</label>
                <input
                  id="limit"
                  type="number"
                  min="1"
                  max="100"
                  value={limit}
                  onChange={e => setLimit(parseInt(e.target.value) || 10)}
                />
              </div>
            )}

            <button type="submit" className="scrape-btn" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Scraping...
                </>
              ) : (
                <>🔍 Start Scraping</>
              )}
            </button>
          </form>

          {/* Error display */}
          {error && (
            <div className="scrape-error">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Results display */}
          {results && (
            <div className="scrape-results">
              <h2>Results</h2>
              {results.success ? (
                <>
                  {/* Profile result */}
                  {scrapeType === 'profile' && results.data && (
                    <ScrapeCard data={results.data} type="profile" />
                  )}

                  {/* Posts/Search results */}
                  {(scrapeType === 'posts' || scrapeType === 'search') && results.data && (
                    <div className="posts-grid">
                      <div className="results-meta">
                        Found {results.count || results.data.length} items
                      </div>
                      {results.data.map((post, idx) => (
                        <ScrapeCard key={idx} data={post} type="post" />
                      ))}
                    </div>
                  )}

                  {/* URL result */}
                  {scrapeType === 'url' && results.data && (
                    <ScrapeCard data={results.data} type="url" />
                  )}
                </>
              ) : (
                <div className="scrape-error">
                  <span>{results.error || 'No data found'}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <style jsx>{`
        .scrape-page {
          display: flex;
          min-height: 100vh;
        }

        .scrape-types {
          padding: 1rem;
        }

        .scrape-types h3 {
          color: var(--text-muted);
          font-size: 0.85rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.75rem;
        }

        .scrape-type-btn {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          width: 100%;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .scrape-type-btn:hover {
          border-color: var(--primary);
        }

        .scrape-type-btn.active {
          background: var(--primary);
          border-color: var(--primary);
        }

        .scrape-type-btn.active .type-label,
        .scrape-type-btn.active .type-desc {
          color: var(--bg);
        }

        .type-label {
          font-weight: 600;
          color: var(--text-light);
        }

        .type-desc {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-top: 0.25rem;
        }

        .back-link {
          display: block;
          padding: 0.75rem 1rem;
          color: var(--primary);
          text-decoration: none;
          transition: opacity 0.2s;
        }

        .back-link:hover {
          opacity: 0.8;
        }

        .scrape-main {
          flex: 1;
        }

        .page-title {
          font-size: 1.75rem;
          color: var(--primary);
          margin: 0;
        }

        .page-subtitle {
          color: var(--text-muted);
          font-size: 0.9rem;
        }

        .scrape-content {
          padding: 2rem;
          max-width: 900px;
        }

        .scrape-form {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.5rem;
          margin-bottom: 2rem;
        }

        .form-group {
          margin-bottom: 1.25rem;
        }

        .form-group label {
          display: block;
          font-weight: 600;
          margin-bottom: 0.5rem;
          color: var(--text-light);
        }

        .form-group input {
          width: 100%;
          padding: 0.75rem 1rem;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          color: var(--text-light);
          font-size: 1rem;
        }

        .form-group input:focus {
          outline: none;
          border-color: var(--primary);
        }

        .platform-selector,
        .engine-selector {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .platform-btn,
        .engine-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 0.75rem 1rem;
          background: var(--bg);
          border: 2px solid var(--border);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          min-width: 90px;
        }

        .platform-btn:hover,
        .engine-btn:hover {
          border-color: var(--primary);
        }

        .platform-btn.active,
        .engine-btn.active {
          border-color: var(--primary);
          background: var(--primary);
        }

        .platform-btn.active .platform-icon,
        .platform-btn.active .platform-label,
        .engine-btn.active .engine-label,
        .engine-btn.active .engine-desc {
          color: var(--bg);
        }

        .platform-icon {
          font-size: 1.5rem;
          margin-bottom: 0.25rem;
        }

        .platform-label,
        .engine-label {
          font-size: 0.85rem;
          color: var(--text-light);
          font-weight: 500;
        }

        .engine-desc {
          font-size: 0.7rem;
          color: var(--text-muted);
          margin-top: 0.2rem;
        }

        .scrape-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          width: 100%;
          padding: 1rem;
          background: var(--primary);
          border: none;
          border-radius: 8px;
          color: var(--bg);
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: filter 0.2s;
        }

        .scrape-btn:hover:not(:disabled) {
          filter: brightness(1.1);
        }

        .scrape-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .spinner {
          width: 20px;
          height: 20px;
          border: 2px solid var(--bg);
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .scrape-error {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem;
          background: #ff4d4d20;
          border: 1px solid #ff4d4d;
          border-radius: 8px;
          color: #ff4d4d;
          margin-bottom: 1rem;
        }

        .scrape-results h2 {
          color: var(--primary);
          margin-bottom: 1rem;
        }

        .results-meta {
          color: var(--text-muted);
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }

        .posts-grid {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        @media (max-width: 900px) {
          .platform-selector {
            flex-direction: column;
          }

          .platform-btn {
            flex-direction: row;
            justify-content: flex-start;
            gap: 0.75rem;
            width: 100%;
          }

          .platform-icon {
            margin-bottom: 0;
          }
        }

        @media (max-width: 650px) {
          .scrape-content {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  );
}
