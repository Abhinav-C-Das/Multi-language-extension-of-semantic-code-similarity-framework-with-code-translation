#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (product = product * arr[i])
 */
long multAll(int arr[], int n) {
  long prod = 1;
  for (int i = 0; i < n; i++) {
    prod = prod * arr[i];
  }
  return prod;
}

int main() {
  int arr[] = {2, 3, 4, 5};
  cout << "Product: " << multAll(arr, 4) << endl;
  return 0;
}
