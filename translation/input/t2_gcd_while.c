#include <stdio.h>

int find_gcd(int a, int b) {
  int temp = 0;
  while (b != 0) {
    temp = b;
    b = a % b;
    a = temp;
  }
  return a;
}

int main() {
  int num1 = 48;
  int num2 = 18;
  int gcd = 0;

  if (num1 < 0 || num2 < 0) {
    printf("Error: Negative numbers not supported.\n");
  } else {
    gcd = find_gcd(num1, num2);
    printf("GCD of %d and %d is %d\n", num1, num2, gcd);
  }
  return 0;
}
