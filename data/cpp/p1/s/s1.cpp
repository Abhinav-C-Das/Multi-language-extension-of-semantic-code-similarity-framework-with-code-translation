#include <iostream>
#include <vector>


/**
 * Student Submission 1
 * Should match: ref1 (indexed for loop with compound assignment)
 */
int simpleSum(const std::vector<int> &arr) {
  int res = 0;
  for (size_t j = 0; j < arr.size(); j++) {
    res += arr[j];
  }
  return res;
}

int main() {
  std::vector<int> test = {10, 20, 30, 40, 50};
  std::cout << "Result: " << simpleSum(test) << std::endl;
  return 0;
}
