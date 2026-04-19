// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

int gcd(int a, int b) {
    while ((b != 0)) {
        int temp = b;
        b = (a % b);
        a = temp;
    }
    return a;
}

int main() {
    printf("GCD(48,18) = %d\n", gcd(48, 18));
    return 0;
}
