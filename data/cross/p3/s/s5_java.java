/**
 * Student 5 — matches ref2 (product = product * arr[i])
 */
public class s5_java {
    public static long productOf(int[] arr) {
        long ans = 1;
        for (int i = 0; i < arr.length; i++) {
            ans = ans * arr[i];
        }
        return ans;
    }

    public static void main(String[] args) {
        int[] d = { 2, 3, 4, 5 };
        System.out.println("Answer: " + productOf(d));
    }
}
