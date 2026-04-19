// Auto-generated from CPG Abstract Program Model
#include <iostream>

int gcd(int a, int b) {
    while ((b != 0)) {
        int temp = b;
        b = (a % b);
        a = temp;
    }
    return a;
}

int main() {
    std::cout << "GCD(48,18) = " << gcd(48, 18) << std::endl;
    return 0;
}
