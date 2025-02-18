import { Router } from "express";
import { fetchTodo } from "./controllers/fetchToDo";
import { addPR } from "./controllers/addPR";
import { checkToDo } from "./controllers/checkToDo";
import type { RequestHandler } from "express";

const router = Router();

router.post("/fetch-to-do", fetchTodo as RequestHandler);
router.post("/add-pr-to-to-do", addPR as RequestHandler);
router.post("/check-to-do", checkToDo as RequestHandler);

export default router;
