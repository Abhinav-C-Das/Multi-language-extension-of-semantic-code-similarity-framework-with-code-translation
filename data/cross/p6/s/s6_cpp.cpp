#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (head recursion)
 */
long getFactorial(int num) {
  if (num <= 1)
    return 1;
  return num * getFactorial(num - 1);
}

int main() {
  cout << "Fact 6: " << getFactorial(6) << endl;
  return 0;
}
