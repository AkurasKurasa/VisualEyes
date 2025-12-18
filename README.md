data structures and algorithms visualizer for leetcode

inspired by not knowing what the hell my code does if i dont see it,
a tendency and inclination for visual learning,
tons of paper wasted in leetcode,
and 2025 advent of code day-9 part 2

## 12 - 18 - 2025
Working 2Sum

pair_idx = {}
nums = [2,7,11,15]
target = 9

for i, num in enumerate(nums):
    if target - num in pair_idx:
        print(i, pair_idx[target - num])
    pair_idx[num] = i
