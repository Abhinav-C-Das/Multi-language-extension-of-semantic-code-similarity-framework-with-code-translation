#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref2 (balance = balance - expenses[i])
 */
int expenseCalc(int init, int exp[], int n) {
  int total = init;
  for (int i = 0; i < n; i++) {
    total = total - exp[i];
  }
  return total;
}

int main() {
  int exp[] = {50, 30, 20, 45, 15};
  cout << "Total: " << expenseCalc(500, exp, 5) << endl;
  return 0;
}
