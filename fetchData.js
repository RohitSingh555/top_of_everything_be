const fs = require('fs');

const categories = {
  Movies: ['Interstellar (film)', 'The Matrix', 'Inception', 'Blade Runner 2049', 'The Godfather', 'Pulp Fiction', 'The Dark Knight', 'Fight Club', 'Forrest Gump', 'Goodfellas', 'The Shawshank Redemption', 'The Lord of the Rings: The Fellowship of the Ring', 'Star Wars (film)', 'Jurassic Park (film)', 'Avengers: Endgame', 'Titanic (1997 film)', 'Avatar (2009 film)', 'Gladiator (2000 film)', 'The Silence of the Lambs (film)', 'Se7en', 'The Departed', 'The Prestige (film)', 'Memento (film)', 'Whiplash (2014 film)', 'Mad Max: Fury Road', 'Parasite (2019 film)', 'Joker (2019 film)', 'Spider-Man: Into the Spider-Verse', 'The Lion King (1994 film)', 'Toy Story'],
  Anime: ['Attack on Titan (TV series)', 'Death Note', 'Fullmetal Alchemist: Brotherhood', 'Naruto', 'One Piece', 'Bleach (TV series)', 'Dragon Ball Z', 'My Hero Academia', 'Demon Slayer: Kimetsu no Yaiba', 'Jujutsu Kaisen', 'Hunter × Hunter', 'Steins;Gate', 'Code Geass', 'Cowboy Bebop', 'Neon Genesis Evangelion', 'Spirited Away', 'Your Name', 'Princess Mononoke', 'Akira (1988 film)', 'Ghost in the Shell (1995 film)'],
  Games: ['The Witcher 3: Wild Hunt', 'Elden Ring', 'Red Dead Redemption 2', 'The Legend of Zelda: Breath of the Wild', 'Grand Theft Auto V', 'Minecraft', 'Tetris', 'Super Mario 64', 'Half-Life 2', 'Portal 2', 'BioShock', 'Mass Effect 2', 'The Elder Scrolls V: Skyrim', 'Dark Souls', 'Bloodborne', 'God of War (2018 video game)', 'The Last of Us', 'Uncharted 4: A Thief\'s End', 'Halo: Combat Evolved', 'Super Smash Bros. Ultimate'],
  Flowers: ['Rose', 'Tulip', 'Orchid', 'Sunflower', 'Lily', 'Daisy', 'Daffodil', 'Marigold', 'Lotus', 'Jasmine', 'Hibiscus', 'Lavender', 'Peony', 'Chrysanthemum', 'Carnation', 'Iris (plant)', 'Poppy', 'Lilac', 'Hydrangea', 'Viola (plant)']
};

async function fetchWikiData(title, category) {
  try {
    const res = await fetch(`https://en.wikipedia.org/w/api.php?action=query&titles=${encodeURIComponent(title)}&prop=pageimages|extracts&exintro=1&explaintext=1&format=json&pithumbsize=600`, {
      headers: { 'User-Agent': 'RankrDataFetcher/1.0 (test@example.com)' }
    });
    const data = await res.json();
    const pages = data.query.pages;
    const page = Object.values(pages)[0];
    
    // Clean up title
    let cleanTitle = page.title.replace(/\s*\(.*?\)\s*/g, '');

    return {
      id: Date.now() + Math.random().toString(36).substring(7),
      name: cleanTitle,
      category,
      image: page.thumbnail?.source || `https://placehold.co/400x600/6CABDD/FFF?text=${encodeURIComponent(cleanTitle)}`,
      description: page.extract ? page.extract.split('\n')[0].substring(0, 200) + '...' : 'A highly rated item in this category.'
    };
  } catch (err) {
    console.error(`Failed to fetch ${title}:`, err.message);
    let cleanTitle = title.replace(/\s*\(.*?\)\s*/g, '');
    return {
      id: Date.now() + Math.random().toString(36).substring(7),
      name: cleanTitle,
      category,
      image: `https://placehold.co/400x600/6CABDD/FFF?text=${encodeURIComponent(cleanTitle)}`,
      description: 'A highly rated item in this category.'
    };
  }
}

async function generateData() {
  const items = [];
  console.log('Fetching data from Wikipedia...');
  
  const promises = [];
  let index = 0;
  for (const [category, names] of Object.entries(categories)) {
    for (const name of names) {
      promises.push(
        new Promise(resolve => setTimeout(resolve, index * 100))
          .then(() => fetchWikiData(name, category))
      );
      index++;
    }
  }

  const results = await Promise.all(promises);
  items.push(...results);

  const fileContent = 'export const SAMPLE_DATA = ' + JSON.stringify(items, null, 2) + ';\n';
  fs.writeFileSync('./rankr-frontend/lib/sampleData.ts', fileContent);
  console.log('Successfully generated sampleData.ts with ' + items.length + ' real entries!');
}

generateData();
