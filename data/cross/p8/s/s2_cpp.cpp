#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (full scan)
 */
int lookup(int arr[], int len, int item) {
  int pos = -1;
  for (int i = 0; i < len; i++) {
    if (arr[i] == item)
      pos = i;
  }
  return pos;
}
int main() {
  int d[] = {1, 2};
  cout << lookup(d, 2, 2) << endl;
  return 0;
}
