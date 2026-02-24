#include <iostream>

/**
 * Student Submission 6
 * Should match: ref2 (while loop with explicit addition)
 */
int totalSum(int arr[], int n) {
  int result = 0;
  int counter = 0;
  while (counter < n) {
    result = result + arr[counter];
    counter++;
  }
  return result;
}

int main() {
  int data[] = {10, 20, 30, 40, 50};
  std::cout << "Sum: " << totalSum(data, 5) << std::endl;
  return 0;
}
