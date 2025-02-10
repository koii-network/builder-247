import express from "express";
import router from "./routes";
import mongoose from "mongoose";
import http from "http";

export const app = express();
const port = 3000;

app.get("/", (req: express.Request, res: express.Response) => {
  res.send("Hello World!");
});

app.use("/api", router);

export async function connectToDatabase() {
  try {
    await mongoose.connect(process.env.MONGODB_URI as string);
    console.log("Connected to MongoDB");
  } catch (error) {
    console.error("Error connecting to MongoDB:", error);
  }
}

export function startServer(): http.Server {
  return app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
  });
}

export default app;
