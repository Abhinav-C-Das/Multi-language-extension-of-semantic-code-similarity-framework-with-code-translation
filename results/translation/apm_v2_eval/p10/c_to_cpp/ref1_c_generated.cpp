// Auto-generated from CPG Abstract Program Model
#include <iostream>

int isPrime(int n) {
    if ((n <= 1)) {
        return 0;
    }
    for (int i = 2; ((i * i) <= n); i++) {
        if (((n % i) == 0)) {
            return 0;
        }
    }
    return 1;
}

int main() {
    std::cout << "Is 17 prime?" << isPrime(17) << std::endl;
    return 0;
}
