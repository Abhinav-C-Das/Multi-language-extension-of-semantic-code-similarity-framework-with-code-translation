#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (tail recursion)
 */
long computeFact(int n, long acc) {
  if (n <= 1)
    return acc;
  return computeFact(n - 1, acc * n);
}

long computeFact(int n) { return computeFact(n, 1); }

int main() {
  cout << "Fact 7: " << computeFact(7) << endl;
  return 0;
}
