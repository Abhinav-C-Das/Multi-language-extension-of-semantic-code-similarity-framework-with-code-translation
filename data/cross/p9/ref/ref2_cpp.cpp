#include <iostream>
using namespace std;

/**
 * Reference 2: Find Max — Recursive
 * CES: rec_ANY::SIMPLE_RECURSIVE::CALL
 */
int recursiveMax(int arr[], int n) {
  if (n == 1)
    return arr[0];
  int sub = recursiveMax(arr, n - 1);
  if (arr[n - 1] > sub)
    return arr[n - 1];
  return sub;
}

int main() {
  int d[] = {1, 5, 2};
  cout << "Max: " << recursiveMax(d, 3) << endl;
  return 0;
}
