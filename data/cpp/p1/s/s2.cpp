#include <iostream>
#include <vector>


/**
 * Student Submission 2
 * Should match: ref2 (range-based for loop with explicit addition)
 */
int getTotal(const std::vector<int> &values) {
  int result = 0;
  for (const auto &val : values) {
    result = result + val;
  }
  return result;
}

int main() {
  std::vector<int> myArray = {10, 20, 30, 40, 50};
  std::cout << "Total: " << getTotal(myArray) << std::endl;
  return 0;
}
