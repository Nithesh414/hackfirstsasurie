// Disease
fetch('http://localhost:5000/predict', { method:'POST' })
  .then(res => res.json())
  .then(data => console.log(data.predictions));

// Bloom
fetch('http://localhost:6000/calendar?month=February')
  .then(res => res.json())
  .then(data => console.log(data.blooms));