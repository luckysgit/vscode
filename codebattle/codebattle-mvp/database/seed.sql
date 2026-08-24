-- Seed Problems for MVP

INSERT INTO problems (id, title, description, difficulty) VALUES
('11111111-1111-1111-1111-111111111111', 'Two Sum', 'Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

**Example:**
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Because nums[0] + nums[1] == 9, we return [0, 1].', 'easy'),
('22222222-2222-2222-2222-222222222222', 'Reverse String', 'Write a function that reverses a string. The input string is given as an array of characters `s`.

You must do this by modifying the input array in-place with O(1) extra memory.

**Example:**
Input: s = ["h","e","l","l","o"]
Output: ["o","l","l","e","h"]', 'easy'),
('33333333-3333-3333-3333-333333333333', 'Fizz Buzz', 'Given an integer `n`, return a string array answer (1-indexed) where:

- answer[i] == "FizzBuzz" if i is divisible by 3 and 5.
- answer[i] == "Fizz" if i is divisible by 3.
- answer[i] == "Buzz" if i is divisible by 5.
- answer[i] == i (as a string) if none of the above conditions are true.

**Example:**
Input: n = 3
Output: ["1","2","Fizz"]', 'easy');

-- Test cases for Two Sum
INSERT INTO test_cases (problem_id, input, expected, is_hidden, order_index) VALUES
('11111111-1111-1111-1111-111111111111', '[2,7,11,15]
9', '[0,1]', false, 0),
('11111111-1111-1111-1111-111111111111', '[3,2,4]
6', '[1,2]', false, 1),
('11111111-1111-1111-1111-111111111111', '[3,3]
6', '[0,1]', true, 2);

-- Test cases for Reverse String
INSERT INTO test_cases (problem_id, input, expected, is_hidden, order_index) VALUES
('22222222-2222-2222-2222-222222222222', '["h","e","l","l","o"]', '["o","l","l","e","h"]', false, 0),
('22222222-2222-2222-2222-222222222222', '["H","a","n","n","a","h"]', '["h","a","n","n","a","H"]', true, 1);

-- Test cases for Fizz Buzz
INSERT INTO test_cases (problem_id, input, expected, is_hidden, order_index) VALUES
('33333333-3333-3333-3333-333333333333', '3', '["1","2","Fizz"]', false, 0),
('33333333-3333-3333-3333-333333333333', '5', '["1","2","Fizz","4","Buzz"]', false, 1),
('33333333-3333-3333-3333-333333333333', '15', '["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]', true, 2);
