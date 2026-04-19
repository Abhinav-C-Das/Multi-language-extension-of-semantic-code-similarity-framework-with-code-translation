// Auto-generated from CPG Abstract Program Model
#include <iostream>

int findMax(int arr[], int n) {
    int max = arr[0];
    for (int i = 1; (i < n); i++) {
        if ((arr[i] > max)) {
            max = arr[i];
        }
    }
    return max;
}

int main() {
    int arr[] = {12, 45, 23, 67, 34, 89, 21};
    std::cout << "Max = " << findMax(arr, 7) << std::endl;
    return 0;
}
