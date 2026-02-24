#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref2 (sum = sum + a[i]*b[i])
 */
int scalarProd(int a[], int b[], int n) {
  int ans = 0;
  for (int i = 0; i < n; i++) {
    ans = ans + a[i] * b[i];
  }
  return ans;
}

int main() {
  int a[] = {1, 3, 5};
  int b[] = {2, 4, 6};
  cout << "SP: " << scalarProd(a, b, 3) << endl;
  return 0;
}
