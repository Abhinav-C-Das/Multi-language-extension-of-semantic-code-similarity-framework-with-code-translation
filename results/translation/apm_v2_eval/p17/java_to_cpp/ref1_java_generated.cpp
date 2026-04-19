// Auto-generated from CPG Abstract Program Model
#include <iostream>

int countOdds(int arr[], int n) {
    int count = 0;
    for (int i = 0; (i < n); i++) {
        if (((arr[i] % 2) != 0)) {
            count++;
        }
    }
    return count;
}

int main() {
    int arr[] = {12, 35, 1, 10, 34, 1};
    int result = countOdds(arr, 6);
    std::cout << "Result: " << result << std::endl;
    return 0;
}
