// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

int factorial(int n) {
    int result = 1;
    for (int i = 1; (i <= n); i++) {
        result *= i;
    }
    return result;
}

int main() {
    printf("5! = %d\n", factorial(5));
    return 0;
}
