// If using Node <18, run: npm install node-fetch@2
// Then uncomment the next line:
// const fetch = require('node-fetch');

const apiKey = 'c25e7f27140e7eb0f3a5ad91a3f77996'; // your new API key
const city = 'London'; // change city as needed
const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;

// Function to fetch weather
async function getWeather() {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error('HTTP Error ' + response.status);
    const data = await response.json();
    console.log(`Weather in ${city}: ${data.weather[0].description}`);
    console.log(`Temperature: ${data.main.temp}°C`);
    console.log(`Humidity: ${data.main.humidity}%`);
  } catch (error) {
    console.error('Error fetching weather:', error);
  }
}

// Call the function
getWeather();