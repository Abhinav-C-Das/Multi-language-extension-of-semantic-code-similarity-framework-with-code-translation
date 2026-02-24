#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (sum += a[i]*b[i])
 */
int dotProd(int x[], int y[], int n) {
  int res = 0;
  for (int i = 0; i < n; i++) {
    res += x[i] * y[i];
  }
  return res;
}

int main() {
  int x[] = {1, 3, 5};
  int y[] = {2, 4, 6};
  cout << "DP: " << dotProd(x, y, 3) << endl;
  return 0;
}
