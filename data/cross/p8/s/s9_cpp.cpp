#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (early exit)
 */
int quickSearch(int arr[], int sz, int key) {
  for (int i = 0; i < sz; i++) {
    if (arr[i] == key)
      return i;
  }
  return -1;
}
int main() {
  int d[] = {1, 2};
  cout << quickSearch(d, 2, 2) << endl;
  return 0;
}
