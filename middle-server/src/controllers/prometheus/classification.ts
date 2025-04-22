import { Request, Response } from "express";

export const classification = async (req: Request, res: Response) => {
  const { repo_url } = req.body;
  try {
    // access http://127.0.0.1:8080/repo_classify with {
    //   "repo_url": repoUrl
    // }
    const response = await fetch("http://127.0.0.1:8080/repo_classify", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ repo_url: repo_url }),
    });
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Error in classification:', error);
    res.status(500).json({ 
      error: 'Failed to process classification request',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};