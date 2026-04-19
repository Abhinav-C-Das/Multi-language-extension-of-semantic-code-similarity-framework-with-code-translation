// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

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
    printf("Index: %d\n", linearSearch(arr, 5, 45));
    return 0;
}
