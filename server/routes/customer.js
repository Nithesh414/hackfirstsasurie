const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());

const flowerData = [
    { name:"Marigold", region:"Chennai", months:["October","November","December","January","February"], intensity:"High" },
    { name:"Sunflower", region:"North India", months:["November","December","January","February","March"], intensity:"Medium" },
    { name:"Jasmine", region:"South India", months:["January","February","March","April","May","June","July","August","September","October","November","December"], intensity:"High" },
    { name:"Lotus", region:"All India", months:["June","July","August","September"], intensity:"Medium" }
];

// GET /calendar?month=February
app.get('/calendar', (req,res)=>{
    const { month } = req.query;
    const blooms = flowerData.filter(f=>f.months.includes(month));
    res.json({ month, blooms });
});

const PORT = 6000;
app.listen(PORT, ()=>console.log(`Bloom API running on port ${PORT}`));