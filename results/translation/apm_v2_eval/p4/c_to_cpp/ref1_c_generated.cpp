// Auto-generated from CPG Abstract Program Model
#include <iostream>

int linearSearch(int arr[], int n, int target) {
    for (int i = 0; (i < n); i++) {
        if ((arr[i] == target)) {
            return i;
        }
    }
    return -1;
}

int main() {
    int arr[] = {10, 23, 45, 67, 89};
    std::cout << "Index: " << linearSearch(arr, 5, 45) << std::endl;
    return 0;
}
