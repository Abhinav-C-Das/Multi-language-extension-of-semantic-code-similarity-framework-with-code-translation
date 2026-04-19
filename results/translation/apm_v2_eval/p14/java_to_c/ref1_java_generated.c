// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

int sumEvens(int arr[], int n) {
    int sum = 0;
    for (int i = 0; (i < n); i++) {
        if (((arr[i] % 2) == 0)) {
            sum += arr[i];
        }
    }
    return sum;
}

int main() {
    int arr[] = {1, 2, 3, 4, 5, 6};
    int result = sumEvens(arr, 6);
    printf("Result: %d\n", result);
    return 0;
}
