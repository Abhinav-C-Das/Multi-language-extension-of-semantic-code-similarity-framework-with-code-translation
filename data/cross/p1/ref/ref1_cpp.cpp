#include <iostream>

/**
 * Reference Implementation 1: Array Sum
 * Strategy: Indexed for loop with compound assignment (+=)
 * Pattern: Traditional C-style iteration
 */
int sumArray(int arr[], int n) {
  int total = 0;
  for (int i = 0; i < n; i++) {
    total += arr[i];
  }
  return total;
}

int main() {
  int numbers[] = {10, 20, 30, 40, 50};
  int result = sumArray(numbers, 5);
  std::cout << "Sum: " << result << std::endl;
  return 0;
}
