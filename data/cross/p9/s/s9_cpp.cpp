#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (iterative)
 */
int iterateMax(int a[], int n) {
  int mv = a[0];
  for (int i = 1; i < n; i++)
    if (a[i] > mv)
      mv = a[i];
  return mv;
}
int main() {
  int d[] = {1, 2};
  cout << iterateMax(d, 2) << endl;
  return 0;
}
