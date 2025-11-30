# Copyright, Terms of Service, and Ethical Scraping Guidelines

## Overview

This document outlines the legal and ethical considerations for operating a news scraping system in Thailand. Following these guidelines is **MANDATORY** to avoid legal issues and maintain good relationships with content providers.

## Core Principles

### 1. Respect Copyright Law

**Thai Copyright Act B.E. 2537 (1994)** protects:
- Original written content
- Images and photographs
- Videos and multimedia
- Database compilations

**What You CAN Do**:
- ✅ Read and parse publicly available RSS feeds
- ✅ Store article metadata (title, URL, publication date)
- ✅ Create short summaries (fair use)
- ✅ Link back to original sources
- ✅ Use for personal research and analysis

**What You CANNOT Do**:
- ❌ Republish full article content without permission
- ❌ Claim content as your own
- ❌ Remove copyright notices
- ❌ Use content for commercial purposes without license
- ❌ Create derivative works without permission

### 2. Respect Terms of Service (ToS)

**Before scraping any website**:

1. **Read the Terms of Service**
   - Look for sections on "automated access" or "scraping"
   - Check for API availability
   - Note any rate limits

2. **Check robots.txt**
   ```
   https://example.com/robots.txt
   ```
   - Respect `Disallow` directives
   - Follow `Crawl-delay` instructions
   - Identify yourself with proper User-Agent

3. **Look for API or RSS Feeds**
   - Many sites provide official APIs
   - RSS feeds are explicitly meant for consumption
   - Use official channels when available

## RSS Feeds: The Legal Way

### Why RSS is Preferred

RSS (Really Simple Syndication) feeds are:
- **Explicitly published** for consumption
- **Legally safe** to read and parse
- **Technically designed** for automated access
- **Widely accepted** by publishers

### RSS Best Practices

```yaml
# Good RSS scraping practices
practices:
  - Use official RSS feed URLs
  - Respect feed update frequency
  - Cache responses to minimize requests
  - Include proper User-Agent
  - Follow HTTP caching headers (ETag, Last-Modified)
  - Implement exponential backoff on errors
  - Don't hammer servers (max 1 request per minute per domain)
```

### Example: Checking robots.txt

```python
# Our scraper automatically checks robots.txt
# Example for Sanook.com:

# https://www.sanook.com/robots.txt
# User-agent: *
# Disallow: /admin/
# Disallow: /private/
# Allow: /feed/
# Crawl-delay: 2

# This means:
# ✅ /feed/ is allowed
# ✅ Must wait 2 seconds between requests
# ❌ /admin/ and /private/ are forbidden
```

## Thai News Sources: Compliance Guide

### Verified RSS Sources

These sources provide official RSS feeds that are safe to use:

#### 1. ThaiPBS (https://news.thaipbs.or.th)
- **RSS Available**: ✅ Yes
- **robots.txt**: Allows feed access
- **ToS**: Allows personal use, attribution required
- **Rate Limit**: No specific limit, be reasonable
- **Attribution**: "ที่มา: ThaiPBS"

#### 2. Manager Online (https://mgronline.com)
- **RSS Available**: ✅ Yes
- **robots.txt**: Allows feed access
- **ToS**: Allows RSS consumption
- **Rate Limit**: Recommended 1 req/min
- **Attribution**: "ที่มา: ผู้จัดการออนไลน์"

#### 3. Sanook (https://www.sanook.com)
- **RSS Available**: ✅ Yes
- **robots.txt**: Allows /feed/ with 2s crawl-delay
- **ToS**: Allows RSS for personal use
- **Rate Limit**: 2 second delay between requests
- **Attribution**: "ที่มา: Sanook.com"

#### 4. Kapook (https://www.kapook.com)
- **RSS Available**: ✅ Yes
- **robots.txt**: Allows feed access
- **ToS**: Allows RSS consumption
- **Rate Limit**: Be reasonable
- **Attribution**: "ที่มา: Kapook.com"

### How to Verify a New Source

Before adding a new news source:

```bash
# 1. Check robots.txt
curl https://example.com/robots.txt

# 2. Look for RSS feed links
# Check website footer or header for RSS icon
# Common paths: /feed/, /rss/, /rss.xml

# 3. Test RSS feed
curl https://example.com/feed/

# 4. Read Terms of Service
# Look for pages like:
# - /terms
# - /tos
# - /legal
# - /privacy
```

## Implementation Requirements

### 1. User-Agent Identification

**REQUIRED**: Always identify your bot

```python
# Good User-Agent
"ThaiNewsBot/1.0 (+https://yourwebsite.com/bot; contact@email.com)"

# Bad User-Agent (don't do this)
"Mozilla/5.0..."  # Pretending to be a browser
```

### 2. Rate Limiting

**REQUIRED**: Implement rate limiting

```python
# Our implementation
SCRAPER_DELAY_SECONDS = 2  # Wait 2 seconds between requests
SCRAPER_MAX_RETRIES = 3    # Don't hammer on errors

# Per-domain rate limiting
# Max 1 request per minute per domain
```

### 3. Respect robots.txt

**REQUIRED**: Check robots.txt before scraping

```python
# Our scraper automatically checks
SCRAPER_RESPECT_ROBOTS_TXT = True

# This is implemented in rss_parser.py
# See check_robots_txt() method
```

### 4. Caching

**REQUIRED**: Cache responses to minimize requests

```python
# Use HTTP caching headers
# - ETag
# - Last-Modified
# - Cache-Control

# Only fetch if content has changed
```

### 5. Error Handling

**REQUIRED**: Handle errors gracefully

```python
# Don't retry indefinitely
# Use exponential backoff
# Log errors for review
# Disable problematic sources automatically
```

## Content Usage Guidelines

### What You Can Store

✅ **Allowed**:
- Article URL
- Publication date
- Author name
- Category/tags
- Short summary (1-2 sentences)
- Metadata (source, language, etc.)

❌ **Not Allowed Without Permission**:
- Full article text
- Images (unless explicitly licensed)
- Videos
- Paywalled content

### Attribution Requirements

**ALWAYS** include attribution when using content:

```markdown
# Good Attribution
"ที่มา: ThaiPBS News (https://news.thaipbs.or.th/article/xxx)"

# For AI-generated content based on news
"อ้างอิงจาก: [ชื่อแหล่งข่าว] (URL)"
```

### Fair Use in Thailand

Thai Copyright Act allows "fair use" for:
- News reporting
- Research and study
- Criticism and review
- Educational purposes

**Requirements for fair use**:
- Use only necessary portions
- Don't harm commercial value
- Provide attribution
- Transform or add value

## AI-Generated Content Considerations

### Using News as Input for AI

✅ **Allowed**:
- Reading news to generate summaries
- Creating original content inspired by news
- Analyzing trends and topics

❌ **Not Allowed**:
- Copying and slightly rewording (plagiarism)
- Claiming AI output as original reporting
- Removing attribution to sources

### Best Practices

1. **Disclose AI Usage**
   ```
   "คอนเทนต์นี้สร้างโดย AI จากข่าวหลายแหล่ง"
   ```

2. **Maintain Attribution**
   ```
   "อ้างอิงจาก: [แหล่งข่าว 1], [แหล่งข่าว 2]"
   ```

3. **Add Original Value**
   - Analysis
   - Commentary
   - Different perspective
   - Aggregation from multiple sources

## Legal Risks and How to Avoid Them

### Risk 1: Copyright Infringement

**Scenario**: Republishing full articles

**Consequence**: 
- Civil lawsuit for damages
- Criminal prosecution (up to 2 years imprisonment)
- Fines up to 200,000 THB

**Prevention**:
- Only store metadata and summaries
- Link to original articles
- Never republish full content

### Risk 2: Terms of Service Violation

**Scenario**: Scraping sites that prohibit it

**Consequence**:
- IP ban
- Legal action for breach of contract
- Damage to reputation

**Prevention**:
- Read and follow ToS
- Use only RSS feeds and APIs
- Respect rate limits

### Risk 3: Server Overload (DoS)

**Scenario**: Too many requests too fast

**Consequence**:
- IP ban
- Potential legal action
- Classified as cyber attack

**Prevention**:
- Implement rate limiting
- Use caching
- Respect crawl-delay
- Monitor request frequency

### Risk 4: Data Privacy Violations

**Scenario**: Collecting personal data

**Consequence**:
- PDPA (Personal Data Protection Act) violations
- Fines up to 5 million THB

**Prevention**:
- Don't collect personal data
- Focus on public news content only
- No user tracking without consent

## Monitoring and Compliance

### Regular Audits

**Monthly**:
- Review sources for ToS changes
- Check robots.txt updates
- Verify attribution is working
- Review error logs

**Quarterly**:
- Legal compliance review
- Update source list
- Review scraping patterns
- Check for complaints

### Incident Response

If you receive a complaint:

1. **Immediate Action**:
   - Stop scraping the source
   - Remove content if requested
   - Document the complaint

2. **Investigation**:
   - Review your practices
   - Check logs
   - Identify the issue

3. **Resolution**:
   - Respond professionally
   - Offer to remove content
   - Update practices
   - Add source to blocklist if needed

4. **Prevention**:
   - Update guidelines
   - Improve checks
   - Train team

## Recommended Practices

### 1. Transparency

- Publish your bot's purpose
- Provide contact information
- Respond to complaints quickly
- Be honest about your usage

### 2. Minimal Impact

- Scrape during off-peak hours
- Use caching aggressively
- Implement circuit breakers
- Monitor server response times

### 3. Value Addition

- Don't just copy content
- Add analysis or commentary
- Aggregate from multiple sources
- Create original insights

### 4. Regular Review

- Update source list quarterly
- Review legal changes
- Check for new APIs
- Monitor industry standards

## Resources

### Legal References

- [Thai Copyright Act B.E. 2537 (1994)](http://www.wipo.int/wipolex/en/text.jsp?file_id=129186)
- [Personal Data Protection Act (PDPA)](https://www.pdpc.or.th/)
- [Computer Crime Act B.E. 2550 (2007)](https://www.etda.or.th/th/Useful-Resource/Electronic-Transactions-Act.aspx)

### Technical Standards

- [robots.txt Specification](https://www.robotstxt.org/)
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)

### Industry Guidelines

- [Google's Webmaster Guidelines](https://developers.google.com/search/docs/advanced/guidelines/webmaster-guidelines)
- [Common Crawl Foundation](https://commoncrawl.org/)

## Conclusion

**Remember**:
- When in doubt, don't scrape
- RSS feeds are your friend
- Always attribute sources
- Respect rate limits
- Add value, don't just copy
- Be a good internet citizen

**Contact a lawyer if**:
- You plan commercial use
- You receive legal notices
- You're unsure about a source
- You want to republish content

This system is designed for **research and personal use**. For commercial use, consult with a legal professional specializing in Thai copyright law.
