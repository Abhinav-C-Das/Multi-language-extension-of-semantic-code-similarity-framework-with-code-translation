#include <iostream>
using namespace std;

/**
 * Reference 1: Factorial — Head Recursion
 * CES: rec_ANY::HEAD_RECURSIVE::ADD
 */
long factorial(int n) {
  if (n <= 1)
    return 1;
  return n * factorial(n - 1);
}

int main() {
  cout << "5! = " << factorial(5) << endl;
  cout << "10! = " << factorial(10) << endl;
  return 0;
}
