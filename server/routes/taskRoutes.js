const express = require("express");
const router = express.Router();
const Task = require("../models/Task");


// GET all tasks
router.get("/", async (req, res) => {
  const tasks = await Task.find();
  res.json(tasks);
});


// POST new task
router.post("/", async (req, res) => {
  const { title, description, due } = req.body;

  const task = new Task({
    title,
    description,
    due
  });

  await task.save();
  res.json({ message: "Task Added" });
});

module.exports = router;