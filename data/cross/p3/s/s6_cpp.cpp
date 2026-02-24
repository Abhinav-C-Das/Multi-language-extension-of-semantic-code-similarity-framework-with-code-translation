#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (product *= arr[i])
 */
long totalProduct(int arr[], int n) {
  long tp = 1;
  for (int i = 0; i < n; i++) {
    tp *= arr[i];
  }
  return tp;
}

int main() {
  int arr[] = {2, 3, 4, 5};
  cout << "TP: " << totalProduct(arr, 4) << endl;
  return 0;
}
