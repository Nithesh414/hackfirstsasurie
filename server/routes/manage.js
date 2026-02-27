const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());

const crops = ["Tomato", "Potato", "Onion", "Chili", "Brinjal"];
const diseases = ["Healthy", "Early Blight", "Leaf Spot", "Powdery Mildew", "Bacterial Wilt"];

// POST /predict
app.post('/predict', (req, res) => {
    // Normally you would handle an image upload and model prediction
    // For demo, we randomly generate predictions
    const predictions = [];
    const count = Math.floor(Math.random()*3)+1;
    for(let i=0;i<count;i++){
        const crop = crops[Math.floor(Math.random()*crops.length)];
        const disease = diseases[Math.floor(Math.random()*diseases.length)];
        predictions.push({ crop, disease });
    }
    res.json({ predictions });
});

const PORT = 5000;
app.listen(PORT, () => console.log(`Disease API running on port ${PORT}`));