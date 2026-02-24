#include <stdio.h>

/**
 * Student 3 — matches ref2 (balance = balance - expenses[i])
 */
int afterExpenses(int init, int exp[], int n) {
  int bal = init;
  for (int i = 0; i < n; i++) {
    bal = bal - exp[i];
  }
  return bal;
}

int main() {
  int exp[] = {50, 30, 20, 45, 15};
  printf("Balance: %d\n", afterExpenses(500, exp, 5));
  return 0;
}
