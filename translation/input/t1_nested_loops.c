#include <stdio.h>

void print_pyramid(int rows) {
  for (int i = 1; i <= rows; i++) {
    for (int j = 1; j <= (rows - i); j++) {
      printf(" ");
    }
    for (int k = 1; k <= (2 * i - 1); k++) {
      printf("*");
    }
    printf("\n");
  }
}

int main() {
  print_pyramid(5);
  return 0;
}
