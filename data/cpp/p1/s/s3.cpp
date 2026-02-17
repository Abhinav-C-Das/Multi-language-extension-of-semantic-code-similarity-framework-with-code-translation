#include <iostream>
#include <vector>


/**
 * Student Submission 3
 * Should match: ref1 (indexed for loop with compound assignment)
 * Different variable names but same computational strategy
 */
int calculateSum(const std::vector<int> &data) {
  int sum = 0;
  for (size_t idx = 0; idx < data.size(); idx++) {
    sum += data[idx];
  }
  return sum;
}

int main() {
  std::vector<int> nums = {10, 20, 30, 40, 50};
  std::cout << "Sum is: " << calculateSum(nums) << std::endl;
  return 0;
}
