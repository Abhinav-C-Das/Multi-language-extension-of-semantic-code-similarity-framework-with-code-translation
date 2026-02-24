#include <stdio.h>

/**
 * Student 8 — matches ref1 (balance -= expenses[i])
 */
int processPayments(int start, int payments[], int n) {
  int bal = start;
  for (int i = 0; i < n; i++) {
    bal -= payments[i];
  }
  return bal;
}

int main() {
  int pay[] = {50, 30, 20, 45, 15};
  printf("Bal: %d\n", processPayments(500, pay, 5));
  return 0;
}
