/**
 * Reference 1: Find Max — Iterative
 * CES: loop_ANY::MAX_UPDATE::COMPARE
 */
public class ref1_java {
    public static int findMax(int[] arr) {
        int max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }

    public static void main(String[] args) {
        System.out.println("Max: " + findMax(new int[] { 1, 5, 2 }));
    }
}
