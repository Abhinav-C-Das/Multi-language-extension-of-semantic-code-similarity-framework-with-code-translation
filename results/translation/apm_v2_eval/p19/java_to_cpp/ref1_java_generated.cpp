// Auto-generated from CPG Abstract Program Model
#include <iostream>

void selectionSort(int arr[], int n) {
    for (int i = 0; (i < (n - 1)); i++) {
        int minIdx = i;
        for (int j = (i + 1); (j < n); j++) {
            if ((arr[j] < arr[minIdx])) {
                minIdx = j;
            }
        }
        int temp = arr[i];
        arr[i] = arr[minIdx];
        arr[minIdx] = temp;
    }
}

int main() {
    int arr[] = {64, 25, 12, 22, 11};
    int n = 5;
    selectionSort(arr, n);
    for (int i = 0; (i < n); i++) {
        std::cout << arr[i] << " ";
    }
    std::cout << std::endl;
    return 0;
}
