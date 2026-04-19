// Auto-generated from CPG Abstract Program Model
#include <iostream>

int factorial(int n) {
    int result = 1;
    for (int i = 1; (i <= n); i++) {
        result *= i;
    }
    return result;
}

int main() {
    std::cout << "5! = " << factorial(5) << std::endl;
    return 0;
}
