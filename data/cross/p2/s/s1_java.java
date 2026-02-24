/**
 * Student 1 — matches ref1 (count += 1)
 */
public class s1_java {
    public static int howMany(int[] arr, int val) {
        int total = 0;
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == val) {
                total += 1;
            }
        }
        return total;
    }

    public static void main(String[] args) {
        int[] nums = { 3, 7, 3, 2, 3, 8, 3, 1 };
        System.out.println("Found: " + howMany(nums, 3));
    }
}
