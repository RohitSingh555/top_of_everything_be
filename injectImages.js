const fs = require('fs');

const realImages = {
  "Interstellar": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/gEU2QniE6E77NI6lCU6MvrId227.jpg",
  "The Matrix": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/f89U3ADr1oiB1s9GvwJwB02xcok.jpg",
  "Inception": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
  "The Godfather": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
  "The Dark Knight": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
  "Pulp Fiction": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
  "Fight Club": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
  "Forrest Gump": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
  "The Lord of the Rings: The Fellowship of the Ring": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
  "Avengers: Endgame": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
  "Spirited Away": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/39wmItIWsg5sZMyRUHLkBg8lWOb.jpg",
  "Your Name": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/q719jXXEzOoYaps6babgKnONONX.jpg",
  "Attack on Titan": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/8jOWn79E2bWqZ2XGk48tYnvZ97X.jpg",
  "Death Note": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/tC3H7XU5cT2tBtcQ31g1jXQpXQy.jpg",
  "The Witcher 3: Wild Hunt": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.png",
  "Elden Ring": "https://images.igdb.com/igdb/image/upload/t_cover_big/co4jni.png",
  "Grand Theft Auto V": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2lbd.png",
  "Minecraft": "https://images.igdb.com/igdb/image/upload/t_cover_big/co49x5.png",
  "Red Dead Redemption 2": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q1f.png",
  "The Legend of Zelda: Breath of the Wild": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.png"
};

const unsplashFallbacks = [
  "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1585647347384-2593bc35786b?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1478720568477-152d9b164e26?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1616530940355-351fabd9524b?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=600&auto=format&fit=crop"
];

let content = fs.readFileSync('./rankr-frontend/lib/sampleData.ts', 'utf8');

// The file exports `SAMPLE_DATA = [...]`. We need to parse it, mutate it, and rewrite it.
const jsonStart = content.indexOf('[');
const jsonEnd = content.lastIndexOf(']') + 1;
const jsonStr = content.substring(jsonStart, jsonEnd);

let data = JSON.parse(jsonStr);

let fallbackIndex = 0;

data = data.map(item => {
  if (realImages[item.name]) {
    item.image = realImages[item.name];
  } else if (item.image.includes('placehold.co')) {
    item.image = unsplashFallbacks[fallbackIndex % unsplashFallbacks.length];
    fallbackIndex++;
  }
  return item;
});

const newContent = 'export const SAMPLE_DATA = ' + JSON.stringify(data, null, 2) + ';\n';
fs.writeFileSync('./rankr-frontend/lib/sampleData.ts', newContent);
console.log('Successfully injected real images and Unsplash fallbacks into sampleData.ts');
