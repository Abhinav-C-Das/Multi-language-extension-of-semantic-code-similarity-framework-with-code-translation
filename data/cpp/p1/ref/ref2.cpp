#include <iostream>
#include <vector>


/**
 * Reference Implementation 2: Array Sum
 * Strategy: Range-based for loop (C++11) with explicit addition
 * Pattern: Iterator-based iteration
 */
int calSum(const std::vector<int> &numbers) {
  int s = 0;
  for (const auto &num : numbers) {
    s = s + num;
  }
  return s;
}

int main() {
  std::vector<int> data = {10, 20, 30, 40, 50};
  int result = calSum(data);
  std::cout << "Sum: " << result << std::endl;
  return 0;
}
