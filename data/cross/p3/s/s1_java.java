/**
 * Student 1 — matches ref1 (product *= arr[i])
 */
public class s1_java {
    public static long multiply(int[] nums) {
        long result = 1;
        for (int i = 0; i < nums.length; i++) {
            result *= nums[i];
        }
        return result;
    }

    public static void main(String[] args) {
        int[] v = { 2, 3, 4, 5 };
        System.out.println("Result: " + multiply(v));
    }
}
