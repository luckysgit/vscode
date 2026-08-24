/* ==========================================================================
   CODEBATTLE — MODULE: PROBLEMS SERVICE & VERSIONING COMMIT SYSTEM
   Location: src/modules/problems/problem.service.js
   ========================================================================== */

class ProblemService {
  constructor() {
    this.STORAGE_KEY_PROBLEMS = 'cb_custom_problems_bank';
    this.STORAGE_KEY_COMMITS = 'cb_problem_commits_history';

    // Default Seed Problem Bank
    this.defaultProblems = [
      {
        id: "p1",
        version: 1,
        title: "Two Sum: Hash Strategy",
        difficulty: "Easy",
        category: "Arrays & Hashes",
        description: "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
        inputFormat: "Line 1: Space-separated integers (nums)\nLine 2: Target integer",
        outputFormat: "Two space-separated indices [index1, index2]",
        solves: 1482,
        avgTime: "4m 12s",
        status: "Passed",
        testCases: [
          { input: "2 7 11 15\n9", expected: "0 1", isHidden: false },
          { input: "3 2 4\n6", expected: "1 2", isHidden: false },
          { input: "3 3\n6", expected: "0 1", isHidden: true }
        ],
        commits: [
          { version: 1, message: "Initial problem commit", timestamp: "2026-07-28T20:00:00Z" }
        ]
      },
      {
        id: "p2",
        version: 1,
        title: "Valid Parentheses Stack",
        difficulty: "Easy",
        category: "Stack & Strings",
        description: "Given a string `s` containing brackets, determine if the string is valid.",
        inputFormat: "Single line string `s`",
        outputFormat: "boolean",
        solves: 2910,
        avgTime: "2m 50s",
        status: "Passed",
        testCases: [
          { input: "()[]{}", expected: "true", isHidden: false },
          { input: "(]", expected: "false", isHidden: false }
        ],
        commits: [
          { version: 1, message: "Initial problem commit", timestamp: "2026-07-28T20:30:00Z" }
        ]
      }
    ];

    this.problems = this.loadProblems();
  }

  loadProblems() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY_PROBLEMS);
      if (saved) return JSON.parse(saved);
    } catch (e) { console.error("Problem bank load error", e); }
    return this.defaultProblems;
  }

  saveProblems() {
    try {
      localStorage.setItem(this.STORAGE_KEY_PROBLEMS, JSON.stringify(this.problems));
    } catch (e) { console.error("Problem bank save error", e); }
  }

  // Create a new problem (Saved in bank for room picker reuse)
  createProblem({ title, difficulty, category, description, inputFormat, outputFormat, testCases, author }) {
    const newProblem = {
      id: "p_custom_" + Date.now(),
      version: 1,
      title: title || "Custom Challenge",
      difficulty: difficulty || "Medium",
      category: category || "General",
      description: description || "Write a solution for this problem.",
      inputFormat: inputFormat || "Input stream",
      outputFormat: outputFormat || "Output value",
      solves: 0,
      avgTime: "--",
      status: "Unsolved",
      author: author || "CodeKnight",
      testCases: testCases || [
        { input: "Sample Input 1", expected: "Sample Output 1", isHidden: false }
      ],
      commits: [
        { version: 1, message: `Initial problem created by ${author || 'CodeKnight'}`, timestamp: new Date().toISOString() }
      ]
    };

    this.problems.unshift(newProblem);
    this.saveProblems();
    return newProblem;
  }

  // Update / Commit changes to an existing problem (Versioning history)
  commitProblemUpdate(problemId, updatedData, commitMessage = "Updated problem testcases") {
    const index = this.problems.findIndex(p => p.id === problemId);
    if (index === -1) return null;

    const current = this.problems[index];
    const newVersion = (current.version || 1) + 1;

    const updatedProblem = {
      ...current,
      ...updatedData,
      version: newVersion,
      commits: [
        ...(current.commits || []),
        { version: newVersion, message: commitMessage, timestamp: new Date().toISOString() }
      ]
    };

    this.problems[index] = updatedProblem;
    this.saveProblems();
    return updatedProblem;
  }

  getAllProblems() {
    return this.problems;
  }

  getProblemById(id) {
    return this.problems.find(p => p.id === id) || this.problems[0];
  }
}

if (typeof window !== 'undefined') {
  window.ProblemService = ProblemService;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProblemService;
}
