import { Router } from "express";
import { fetchTodo } from "./controllers/fetchToDo";
// import { createTodo } from "./controllers/createToDo";
import { addPR } from "./controllers/addPR";
import { checkToDo } from "./controllers/checkToDo";
const router = Router();

router.post("/fetch-to-do", fetchTodo);
// router.post("/create-to-do", createTodo);
router.post("/add-pr-to-to-do", addPR);
router.post("/check-to-do", checkToDo);

export default router;
