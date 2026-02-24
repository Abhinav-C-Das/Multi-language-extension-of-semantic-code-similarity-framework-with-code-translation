#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (recursive)
 */
int getPeak(int a[], int sz) {
  if (sz == 1)
    return a[0];
  int s = getPeak(a, sz - 1);
  return (a[sz - 1] > s) ? a[sz - 1] : s;
}
int main() {
  int d[] = {1, 2};
  cout << getPeak(d, 2) << endl;
  return 0;
}
