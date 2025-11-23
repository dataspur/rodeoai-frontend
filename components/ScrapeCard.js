/**
 * ScrapeCard Component
 * Displays scraped social media data in a beautiful card format.
 */

export default function ScrapeCard({ data, type }) {
  if (!data) return null;

  // Profile card
  if (type === 'profile') {
    return (
      <div className="scrape-card profile-card">
        <div className="profile-header">
          {data.profile_image_url && (
            <img
              src={data.profile_image_url}
              alt={data.display_name}
              className="profile-avatar"
            />
          )}
          <div className="profile-info">
            <h3 className="profile-name">
              {data.display_name}
              {data.verified && <span className="verified-badge" title="Verified">✓</span>}
            </h3>
            <span className="profile-handle">@{data.username}</span>
            <span className="profile-platform">{data.platform}</span>
          </div>
        </div>
        {data.bio && <p className="profile-bio">{data.bio}</p>}
        <div className="profile-stats">
          {data.followers !== undefined && (
            <div className="stat">
              <span className="stat-value">{formatCount(data.followers)}</span>
              <span className="stat-label">Followers</span>
            </div>
          )}
          {data.following !== undefined && (
            <div className="stat">
              <span className="stat-value">{formatCount(data.following)}</span>
              <span className="stat-label">Following</span>
            </div>
          )}
          {data.post_count !== undefined && data.post_count > 0 && (
            <div className="stat">
              <span className="stat-value">{formatCount(data.post_count)}</span>
              <span className="stat-label">Posts</span>
            </div>
          )}
        </div>
        {data.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer" className="profile-link">
            View Profile →
          </a>
        )}
      </div>
    );
  }

  // Post card
  if (type === 'post') {
    return (
      <div className="scrape-card post-card">
        <div className="post-header">
          <span className="post-author">
            {data.author_handle || data.author}
          </span>
          <span className="post-platform">{data.platform}</span>
        </div>
        <p className="post-content">{data.content}</p>
        {data.media_urls && data.media_urls.length > 0 && (
          <div className="post-media">
            {data.media_urls.slice(0, 4).map((url, idx) => (
              <img key={idx} src={url} alt="" className="post-media-item" />
            ))}
          </div>
        )}
        <div className="post-engagement">
          {data.likes !== undefined && (
            <span className="engagement-item">❤️ {formatCount(data.likes)}</span>
          )}
          {data.comments !== undefined && (
            <span className="engagement-item">💬 {formatCount(data.comments)}</span>
          )}
          {data.shares !== undefined && (
            <span className="engagement-item">🔄 {formatCount(data.shares)}</span>
          )}
        </div>
        {data.timestamp && (
          <span className="post-timestamp">{formatDate(data.timestamp)}</span>
        )}
        {data.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer" className="post-link">
            View Original →
          </a>
        )}
      </div>
    );
  }

  // Article card
  if (type === 'article') {
    return (
      <div className="scrape-card article-card">
        <h3 className="article-title">{data.title}</h3>
        {data.author && <span className="article-author">By {data.author}</span>}
        {data.publish_date && (
          <span className="article-date">{data.publish_date}</span>
        )}
        {data.content && (
          <p className="article-excerpt">
            {data.content.substring(0, 500)}...
          </p>
        )}
        {data.word_count && (
          <span className="article-wordcount">{data.word_count} words</span>
        )}
        {data.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer" className="article-link">
            Read Full Article →
          </a>
        )}
      </div>
    );
  }

  // Generic URL scrape result
  if (type === 'url') {
    return (
      <div className="scrape-card url-card">
        <h3 className="url-title">{data.title || 'Scraped Page'}</h3>
        {data.description && <p className="url-description">{data.description}</p>}
        {data.og_data && data.og_data.image && (
          <img src={data.og_data.image} alt="" className="url-preview-image" />
        )}
        {data.headings && data.headings.length > 0 && (
          <div className="url-headings">
            <strong>Headings:</strong>
            <ul>
              {data.headings.slice(0, 5).map((h, idx) => (
                <li key={idx}>{h.text}</li>
              ))}
            </ul>
          </div>
        )}
        {data.links && data.links.length > 0 && (
          <div className="url-links-count">
            Found {data.links.length} links
          </div>
        )}
        <a href={data.url} target="_blank" rel="noopener noreferrer" className="url-link">
          Visit Page →
        </a>
      </div>
    );
  }

  // Fallback: show raw JSON
  return (
    <div className="scrape-card raw-card">
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

// Helper functions
function formatCount(num) {
  if (num === undefined || num === null) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateStr;
  }
}
