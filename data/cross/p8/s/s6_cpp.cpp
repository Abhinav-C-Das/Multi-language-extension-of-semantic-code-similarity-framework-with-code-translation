#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (early exit)
 */
int fastFind(int a[], int n, int v) {
  for (int i = 0; i < n; i++) {
    if (a[i] == v)
      return i;
  }
  return -1;
}
int main() {
  int d[] = {1, 2};
  cout << fastFind(d, 2, 2) << endl;
  return 0;
}
