// Auto-generated from CPG Abstract Program Model
#include <iostream>

int removeDuplicates(int arr[], int n) {
    if (((n == 0) || (n == 1))) {
        return n;
    }
    int j = 0;
    for (int i = 0; (i < (n - 1)); i++) {
        if ((arr[i] != arr[(i + 1)])) {
            arr[j++] = arr[i];
        }
    }
    arr[j++] = arr[(n - 1)];
    return j;
}

int main() {
    int arr[] = {1, 2, 2, 3, 4, 4, 4, 5};
    int n = removeDuplicates(arr, 8);
    std::cout << "Unique Count = " << n << std::endl;
    return 0;
}
