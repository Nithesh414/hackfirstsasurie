const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  phone: String,
  password: String,
  userType: String
}, { timestamps: true });

module.exports = mongoose.model("User", userSchema);