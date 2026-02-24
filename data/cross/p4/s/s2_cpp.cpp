#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref1 (sum += a[i]*b[i])
 */
int innerProd(int a[], int b[], int n) {
  int s = 0;
  for (int i = 0; i < n; i++) {
    s += a[i] * b[i];
  }
  return s;
}

int main() {
  int a[] = {1, 3, 5};
  int b[] = {2, 4, 6};
  cout << "IP: " << innerProd(a, b, 3) << endl;
  return 0;
}
