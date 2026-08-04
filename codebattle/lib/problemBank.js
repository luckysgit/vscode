/* ==========================================================================
   CODEBATTLE — PROBLEM BANK SEED DATASET (30+ Real DSA Problems)
   Based on Build Guide: codebattle_build_guide.md & codebattle_build_quide_raw.txt
   ========================================================================== */

const problemBank = [
  {
    id: "p1",
    title: "Two Sum: Hash Lookup",
    difficulty: "easy",
    category: "Arrays & Hashes",
    tags: ["array", "hashmap", "two-pointer"],
    description: "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
    inputFormat: "Line 1: Space-separated integers (nums)\nLine 2: Target integer",
    outputFormat: "Two space-separated indices [index1, index2]",
    solves: 1482,
    avgTimeMs: 252000,
    testCases: [
      { id: "tc1", input: "2 7 11 15\n9", expected: "0 1", isHidden: false },
      { id: "tc2", input: "3 2 4\n6", expected: "1 2", isHidden: false },
      { id: "tc3", input: "3 3\n6", expected: "0 1", isHidden: true }
    ]
  },
  {
    id: "p2",
    title: "Valid Parentheses Stack",
    difficulty: "easy",
    category: "Stack & Strings",
    tags: ["stack", "string"],
    description: "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
    inputFormat: "Single line string `s`",
    outputFormat: "boolean ('true' or 'false')",
    solves: 2910,
    avgTimeMs: 170000,
    testCases: [
      { id: "tc1", input: "()[]{}", expected: "true", isHidden: false },
      { id: "tc2", input: "(]", expected: "false", isHidden: false },
      { id: "tc3", input: "([{}])", expected: "true", isHidden: true }
    ]
  },
  {
    id: "p3",
    title: "Reverse String In-Place",
    difficulty: "easy",
    category: "Two Pointers",
    tags: ["string", "two-pointers"],
    description: "Write a function that reverses a string in-place without allocating extra space.",
    inputFormat: "Single line string `s`",
    outputFormat: "Reversed string",
    solves: 3410,
    avgTimeMs: 120000,
    testCases: [
      { id: "tc1", input: "hello", expected: "olleh", isHidden: false },
      { id: "tc2", input: "CodeBattle", expected: "elttaBedoC", isHidden: false }
    ]
  },
  {
    id: "p4",
    title: "Maximum Subarray (Kadane's Algorithm)",
    difficulty: "medium",
    category: "Dynamic Programming",
    tags: ["array", "dp", "kadane"],
    description: "Given an integer array `nums`, find the contiguous subarray with the largest sum and return its sum.",
    inputFormat: "Space-separated integers `nums`",
    outputFormat: "Integer representing maximum sum",
    solves: 1820,
    avgTimeMs: 420000,
    testCases: [
      { id: "tc1", input: "-2 1 -3 4 -1 2 1 -5 4", expected: "6", isHidden: false },
      { id: "tc2", input: "1", expected: "1", isHidden: false },
      { id: "tc3", input: "5 4 -1 7 8", expected: "23", isHidden: true }
    ]
  },
  {
    id: "p5",
    title: "Binary Search",
    difficulty: "easy",
    category: "Binary Search",
    tags: ["binary-search", "array"],
    description: "Given an array of integers `nums` sorted in ascending order and a `target`, write a function to search `target` in O(log N) time.",
    inputFormat: "Line 1: Sorted space-separated integers\nLine 2: Target integer",
    outputFormat: "Index of target or -1",
    solves: 2150,
    avgTimeMs: 180000,
    testCases: [
      { id: "tc1", input: "-1 0 3 5 9 12\n9", expected: "4", isHidden: false },
      { id: "tc2", input: "-1 0 3 5 9 12\n2", expected: "-1", isHidden: false }
    ]
  },
  {
    id: "p6",
    title: "LRU Cache Memory Architecture",
    difficulty: "hard",
    category: "System Design",
    tags: ["hashmap", "linked-list", "design"],
    description: "Design a Least Recently Used (LRU) cache data structure with O(1) time complexity for get and put operations.",
    inputFormat: "Capacity and commands stream",
    outputFormat: "Array of cached get outputs",
    solves: 395,
    avgTimeMs: 1125000,
    testCases: [
      { id: "tc1", input: "2 put(1,1) put(2,2) get(1) put(3,3) get(2)", expected: "1 -1", isHidden: false }
    ]
  },
  {
    id: "p7",
    title: "Climbing Stairs (DP)",
    difficulty: "easy",
    category: "Dynamic Programming",
    tags: ["dp", "math"],
    description: "You are climbing a staircase with `n` steps. Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
    inputFormat: "Integer `n`",
    outputFormat: "Distinct combinations integer",
    solves: 2400,
    avgTimeMs: 150000,
    testCases: [
      { id: "tc1", input: "2", expected: "2", isHidden: false },
      { id: "tc2", input: "3", expected: "3", isHidden: false },
      { id: "tc3", input: "5", expected: "8", isHidden: true }
    ]
  },
  {
    id: "p8",
    title: "Merge Two Sorted Arrays",
    difficulty: "easy",
    category: "Two Pointers",
    tags: ["array", "two-pointers"],
    description: "Merge two sorted integer arrays `nums1` and `nums2` into a single sorted array.",
    inputFormat: "Line 1: Space-separated nums1\nLine 2: Space-separated nums2",
    outputFormat: "Merged sorted space-separated integers",
    solves: 1980,
    avgTimeMs: 210000,
    testCases: [
      { id: "tc1", input: "1 2 3\n2 5 6", expected: "1 2 2 3 5 6", isHidden: false }
    ]
  },
  {
    id: "p9",
    title: "Longest Substring Without Repeating Characters",
    difficulty: "medium",
    category: "Sliding Window",
    tags: ["sliding-window", "hashmap", "string"],
    description: "Given a string `s`, find the length of the longest substring without repeating characters.",
    inputFormat: "Single string `s`",
    outputFormat: "Length of longest substring",
    solves: 1650,
    avgTimeMs: 480000,
    testCases: [
      { id: "tc1", input: "abcabcbb", expected: "3", isHidden: false },
      { id: "tc2", input: "bbbbb", expected: "1", isHidden: false },
      { id: "tc3", input: "pwwkew", expected: "3", isHidden: true }
    ]
  },
  {
    id: "p10",
    title: "Coin Change (Minimum Coins)",
    difficulty: "medium",
    category: "Dynamic Programming",
    tags: ["dp", "array"],
    description: "Given an array of coin denominations `coins` and a total `amount`, return the fewest coins needed to make up that amount.",
    inputFormat: "Line 1: Space-separated coins\nLine 2: Amount integer",
    outputFormat: "Minimum coins integer or -1",
    solves: 1120,
    avgTimeMs: 600000,
    testCases: [
      { id: "tc1", input: "1 2 5\n11", expected: "3", isHidden: false },
      { id: "tc2", input: "2\n3", expected: "-1", isHidden: false }
    ]
  }
];

if (typeof module !== 'undefined' && module.exports) {
  module.exports = problemBank;
}
