#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (head recursion)
 */
long nFactorial(int n) {
  if (n <= 1)
    return 1;
  return n * nFactorial(n - 1);
}

int main() {
  cout << "Fact 8: " << nFactorial(8) << endl;
  return 0;
}
