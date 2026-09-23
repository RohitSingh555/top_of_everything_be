const fs = require('fs');

async function scrapeWiki(title) {
  try {
    const url = `https://en.wikipedia.org/wiki/${encodeURIComponent(title.replace(/ /g, '_'))}`;
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    if (!res.ok) return null;
    const html = await res.text();
    
    // Look for the infobox image which usually contains the poster/cover
    const match = html.match(/class="infobox-image"[^>]*>.*?<img[^>]*src="(\/\/upload\.wikimedia\.org\/wikipedia\/(en|commons)\/[^"]+)"/i) || 
                  html.match(/class="infobox[^>]*>.*?<img[^>]*src="(\/\/upload\.wikimedia\.org\/wikipedia\/(en|commons)\/[^"]+)"/i);
    
    if (match) {
      return 'https:' + match[1].replace(/\/\d+px-/, '/600px-'); // Try to get a higher res version
    }
    return null;
  } catch (err) {
    return null;
  }
}

async function fetchAnime(title) {
  try {
    const cleanTitle = title.replace(/\s*\(.*?\)\s*/g, '');
    const res = await fetch(`https://api.jikan.moe/v4/anime?q=${encodeURIComponent(cleanTitle)}&limit=1`);
    if (!res.ok) return null;
    const data = await res.json();
    if (data.data && data.data.length > 0) {
      return data.data[0].images.jpg.large_image_url;
    }
    return null;
  } catch(err) {
    return null;
  }
}

async function run() {
  let content = fs.readFileSync('./rankr-frontend/lib/sampleData.ts', 'utf8');
  const jsonStart = content.indexOf('[');
  const jsonEnd = content.lastIndexOf(']') + 1;
  const jsonStr = content.substring(jsonStart, jsonEnd);
  
  let data = JSON.parse(jsonStr);
  
  for (let i = 0; i < data.length; i++) {
    const item = data[i];
    console.log(`Processing: ${item.name}`);
    
    if (item.category === 'Anime') {
      const img = await fetchAnime(item.name);
      if (img) item.image = img;
    } else {
      // Try to scrape Wikipedia for the exact name or name + category suffix
      let suffix = '';
      if (item.category === 'Movies') suffix = ' (film)';
      if (item.category === 'Games') suffix = ' (video game)';
      
      let img = await scrapeWiki(item.name);
      if (!img && suffix) {
        img = await scrapeWiki(item.name + suffix);
      }
      
      if (img) item.image = img;
    }
    
    // Slight delay to avoid hammering Wikipedia
    await new Promise(r => setTimeout(r, 500));
  }
  
  const newContent = 'export const SAMPLE_DATA = ' + JSON.stringify(data, null, 2) + ';\n';
  fs.writeFileSync('./rankr-frontend/lib/sampleData.ts', newContent);
  console.log('Successfully injected genuine Wikipedia/MyAnimeList images!');
}

run();
