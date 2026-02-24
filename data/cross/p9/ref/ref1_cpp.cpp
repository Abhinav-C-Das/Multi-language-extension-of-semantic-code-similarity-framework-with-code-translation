#include <iostream>
using namespace std;

/**
 * Reference 1: Find Max — Iterative
 * CES: loop_ANY::MAX_UPDATE::COMPARE
 */
int findMaximum(int arr[], int n) {
  int maxVal = arr[0];
  for (int i = 1; i < n; i++) {
    if (arr[i] > maxVal) {
      maxVal = arr[i];
    }
  }
  return maxVal;
}

int main() {
  int d[] = {1, 5, 2};
  cout << "Max: " << findMaximum(d, 3) << endl;
  return 0;
}
