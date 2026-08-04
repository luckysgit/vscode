/* ==========================================================================
   CODEBATTLE — SHARED CONSTANTS & LANGUAGE TEMPLATES
   Location: src/shared/constants/languages.js
   ========================================================================== */

const SUPPORTED_LANGUAGES = [
  { id: "python", name: "Python 3.11", icon: "🐍", ext: "py" },
  { id: "javascript", name: "JavaScript (Node.js)", icon: "⚡", ext: "js" },
  { id: "typescript", name: "TypeScript", icon: "📘", ext: "ts" },
  { id: "cpp", name: "C++ 20", icon: "⚙️", ext: "cpp" },
  { id: "java", name: "Java 21", icon: "☕", ext: "java" },
  { id: "rust", name: "Rust 1.75", icon: "🦀", ext: "rs" },
  { id: "go", name: "Go 1.22", icon: "🐹", ext: "go" },
  { id: "csharp", name: "C# (.NET 8)", icon: "🔷", ext: "cs" },
  { id: "php", name: "PHP 8.3", icon: "🐘", ext: "php" },
  { id: "swift", name: "Swift 5.9", icon: "🍎", ext: "swift" }
];

const STARTER_CODE_TEMPLATES = {
  python: `class Solution:\n    def solve(self, nums: list[int], target: int) -> list[int]:\n        # Write your solution here\n        seen = {}\n        for i, num in enumerate(nums):\n            diff = target - num\n            if diff in seen:\n                return [seen[diff], i]\n            seen[num] = i\n        return []`,

  javascript: `function solve(nums, target) {\n    // Write your solution here\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const diff = target - nums[i];\n        if (map.has(diff)) return [map.get(diff), i];\n        map.set(nums[i], i);\n    }\n    return [];\n}`,

  typescript: `function solve(nums: number[], target: number): number[] {\n    // Write your solution here\n    const map = new Map<number, number>();\n    for (let i = 0; i < nums.length; i++) {\n        const diff = target - nums[i];\n        if (map.has(diff)) return [map.get(diff)!, i];\n        map.set(nums[i], i);\n    }\n    return [];\n}`,

  cpp: `#include <vector>\n#include <unordered_map>\n\nclass Solution {\npublic:\n    std::vector<int> solve(std::vector<int>& nums, int target) {\n        std::unordered_map<int, int> map;\n        for (int i = 0; i < nums.size(); ++i) {\n            int diff = target - nums[i];\n            if (map.count(diff)) return {map[diff], i};\n            map[nums[i]] = i;\n        }\n        return {};\n    }\n};`,

  java: `import java.util.HashMap;\n\nclass Solution {\n    public int[] solve(int[] nums, int target) {\n        HashMap<Integer, Integer> map = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int diff = target - nums[i];\n            if (map.containsKey(diff)) return new int[]{map.get(diff), i};\n            map.put(nums[i], i);\n        }\n        return new int[]{};\n    }\n}`,

  rust: `use std::collections::HashMap;\n\nimpl Solution {\n    pub fn solve(nums: Vec<i32>, target: i32) -> Vec<i32> {\n        let mut map = HashMap::new();\n        for (i, &num) in nums.iter().enumerate() {\n            if let Some(&prev) = map.get(&(target - num)) {\n                return vec![prev as i32, i as i32];\n            }\n            map.insert(num, i);\n        }\n        vec![]\n    }\n}`,

  go: `func solve(nums []int, target int) []int {\n    seen := make(map[int]int)\n    for i, num := range nums {\n        if prev, ok := seen[target-num]; ok {\n            return []int{prev, i}\n        }\n        seen[num] = i\n    }\n    return nil\n}`,

  csharp: `using System.Collections.Generic;\n\npublic class Solution {\n    public int[] Solve(int[] nums, int target) {\n        var map = new Dictionary<int, int>();\n        for (int i = 0; i < nums.Length; i++) {\n            int diff = target - nums[i];\n            if (map.ContainsKey(diff)) return new int[] { map[diff], i };\n            map[nums[i]] = i;\n        }\n        return new int[0];\n    }\n}`,

  php: `class Solution {\n    function solve($nums, $target) {\n        $map = [];\n        foreach ($nums as $i => $num) {\n            $diff = $target - $num;\n            if (array_key_exists($diff, $map)) return [$map[$diff], $i];\n            $map[$num] = $i;\n        }\n        return [];\n    }\n}`,

  swift: `class Solution {\n    func solve(_ nums: [Int], _ target: Int) -> [Int] {\n        var dict = [Int: Int]()\n        for (i, num) in nums.enumerated() {\n            if let prev = dict[target - num] { return [prev, i] }\n            dict[num] = i\n        }\n        return []\n    }\n}`
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SUPPORTED_LANGUAGES, STARTER_CODE_TEMPLATES };
}
