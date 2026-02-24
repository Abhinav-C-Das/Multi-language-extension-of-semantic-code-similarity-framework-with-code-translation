/**
 * Reference 2: Find Max — Recursive
 * CES: rec_ANY::SIMPLE_RECURSIVE::CALL
 */
public class ref2_java {
    public static int findMax(int[] arr, int n) {
        if (n == 1)
            return arr[0];
        int subMax = findMax(arr, n - 1);
        if (arr[n - 1] > subMax)
            return arr[n - 1];
        return subMax;
    }

    public static void main(String[] args) {
        System.out.println("Max: " + findMax(new int[] { 1, 5, 2 }, 3));
    }
}
