const csv = require("csv-parse");
const fs = require("fs");
const mongoose = require("mongoose");
const path = require("path");
require("dotenv").config();

// Configuration
const REPO_OWNER = "koii-network";
const REPO_NAME = "builder-test";
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017/todos";
const CSV_FILE_PATH = path.join(__dirname, "../data/todos.csv");

async function connectToDatabase() {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log("Connected to MongoDB successfully");
  } catch (error) {
    console.error("Failed to connect to MongoDB:", error);
    process.exit(1);
  }
}

async function importTodos() {
  const todoSchema = new mongoose.Schema(
    {
      title: String,
      acceptanceCriteria: String,
      repoOwner: String,
      repoName: String,
      assignedTo: Array,
    },
    { timestamps: true },
  );

  const Todo = mongoose.model("Todo", todoSchema);

  const records = [];

  // Read and parse CSV
  const parser = fs.createReadStream(CSV_FILE_PATH).pipe(
    csv.parse({
      columns: true,
      skip_empty_lines: true,
    }),
  );

  for await (const record of parser) {
    records.push({
      title: record.title,
      acceptanceCriteria: record.acceptanceCriteria,
    });
  }

  console.log(`Found ${records.length} todos to import`);

  // Import records to MongoDB
  try {
    for (const record of records) {
      await Todo.create({
        title: record.title,
        acceptanceCriteria: record.acceptanceCriteria,
        repoOwner: REPO_OWNER,
        repoName: REPO_NAME,
        assignedTo: [],
      });
      console.log(`Imported todo: ${record.title}`);
    }
    console.log("Import completed successfully");
  } catch (error) {
    console.error("Error importing todos:", error);
  }
}

// Run the import
connectToDatabase()
  .then(() => importTodos())
  .then(() => {
    console.log("Script completed");
    process.exit(0);
  })
  .catch((error) => {
    console.error("Script failed:", error);
    process.exit(1);
  });
