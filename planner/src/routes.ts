import { Router } from "express";
import { fetchTodo } from "./controllers/fetchToDo";
import { createTodo } from "./controllers/createToDo";
import { addPRToTODO } from "./controllers/addPRToToDo";
const router = Router();

router.get("/fetch-to-do", fetchTodo);
router.get("/create-to-do", createTodo);
router.get("/add-pr-to-to-do", addPRToTODO);

export default router;
