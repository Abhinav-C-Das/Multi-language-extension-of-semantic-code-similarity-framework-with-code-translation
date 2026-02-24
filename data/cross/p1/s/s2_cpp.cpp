#include <iostream>

/**
 * Student Submission 2
 * Should match: ref1 (indexed for loop with compound assignment)
 * Different variable names but same computational strategy
 */
int addAll(int nums[], int len) {
  int res = 0;
  for (int j = 0; j < len; j++) {
    res += nums[j];
  }
  return res;
}

int main() {
  int arr[] = {10, 20, 30, 40, 50};
  std::cout << "Total: " << addAll(arr, 5) << std::endl;
  return 0;
}
