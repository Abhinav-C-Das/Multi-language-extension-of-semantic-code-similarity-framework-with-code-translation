#include <iostream>

/**
 * Student Submission 9
 * Should match: ref1 (indexed for loop with compound assignment)
 */
int calculateTotal(int elements[], int size) {
  int sum = 0;
  for (int idx = 0; idx < size; idx++) {
    sum += elements[idx];
  }
  return sum;
}

int main() {
  int list[] = {10, 20, 30, 40, 50};
  std::cout << "Answer: " << calculateTotal(list, 5) << std::endl;
  return 0;
}
