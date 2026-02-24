#include <iostream>
using namespace std;

/**
 * Reference 2: Factorial — Tail Recursion with accumulator
 * CES: rec_ANY::TAIL_RECURSIVE::ACCUMULATE
 */
long factorialHelper(int n, long acc) {
  if (n <= 1)
    return acc;
  return factorialHelper(n - 1, acc * n);
}

long factorial(int n) { return factorialHelper(n, 1); }

int main() {
  cout << "5! = " << factorial(5) << endl;
  cout << "10! = " << factorial(10) << endl;
  return 0;
}
