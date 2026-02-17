#include <iostream>
#include <vector>


/**
 * Reference Implementation 1: Array Sum
 * Strategy: Indexed for loop with compound assignment (+=)
 * Pattern: Traditional C-style iteration
 */
int sumArray(const std::vector<int> &arr) {
  int total = 0;
  for (size_t i = 0; i < arr.size(); i++) {
    total += arr[i];
  }
  return total;
}

int main() {
  std::vector<int> numbers = {10, 20, 30, 40, 50};
  int result = sumArray(numbers);
  std::cout << "Sum: " << result << std::endl;
  return 0;
}
