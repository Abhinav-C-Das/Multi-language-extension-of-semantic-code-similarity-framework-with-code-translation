#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (product *= arr[i])
 */
long getProduct(int v[], int n) {
  long res = 1;
  for (int i = 0; i < n; i++) {
    res *= v[i];
  }
  return res;
}

int main() {
  int v[] = {2, 3, 4, 5};
  cout << "Prod: " << getProduct(v, 4) << endl;
  return 0;
}
