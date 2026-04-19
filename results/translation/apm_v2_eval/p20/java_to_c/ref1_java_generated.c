// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

int countPositives(int arr[], int n) {
    int count = 0;
    for (int i = 0; (i < n); i++) {
        if ((arr[i] > 0)) {
            count++;
        }
    }
    return count;
}

int main() {
    int arr[] = {-1, 2, -3, 4, 5, -6};
    int result = countPositives(arr, 6);
    printf("Result: %d\n", result);
    return 0;
}
