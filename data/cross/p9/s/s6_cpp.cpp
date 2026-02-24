#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (iterative)
 */
int largest(int v[], int sz) {
  int lead = v[0];
  for (int i = 1; i < sz; i++) {
    if (v[i] > lead)
      lead = v[i];
  }
  return lead;
}
int main() {
  int d[] = {1, 2};
  cout << largest(d, 2) << endl;
  return 0;
}
