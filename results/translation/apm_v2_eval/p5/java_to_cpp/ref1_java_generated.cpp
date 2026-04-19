// Auto-generated from CPG Abstract Program Model
#include <iostream>

void reverseArray(int arr[], int n) {
    int left;
    int right;
    left = 0;
    right = (n - 1);
    while ((left < right)) {
        int temp = arr[left];
        arr[left] = arr[right];
        arr[right] = temp;
        left++;
        right--;
    }
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    reverseArray(arr, 5);
    for (int i = 0; (i < 5); i++) {
        std::cout << arr[i] << " ";
    }
    return 0;
}
