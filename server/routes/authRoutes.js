const express = require("express");
const bcrypt = require("bcryptjs");
const User = require("../models/User");
const router = express.Router();

/* REGISTER */
router.post("/register", async (req, res) => {
  const { name, email, phone, password, userType } = req.body;

  try {
    const existingUser = await User.findOne({ email });
    if (existingUser)
      return res.status(400).json({ message: "User already exists" });

    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = new User({
      name,
      email,
      phone,
      password: hashedPassword,
      userType
    });

    await newUser.save();
    res.json({ message: "User registered successfully" });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* LOGIN */
router.post("/login", async (req, res) => {
  const { email, password, userType } = req.body;

  try {
    const user = await User.findOne({ email, userType });
    if (!user)
      return res.status(400).json({ message: "User not found" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch)
      return res.status(400).json({ message: "Invalid password" });

    res.json({
      message: "Login successful",
      user
    });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;