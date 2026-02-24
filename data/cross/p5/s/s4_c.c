#include <stdio.h>

/**
 * Student 4 — matches ref1 (balance -= expenses[i])
 */
int deduct(int init, int bills[], int n) {
  int money = init;
  for (int i = 0; i < n; i++) {
    money -= bills[i];
  }
  return money;
}

int main() {
  int bills[] = {50, 30, 20, 45, 15};
  printf("Money: %d\n", deduct(500, bills, 5));
  return 0;
}
