/**
 * Student Submission 5
 * Should match: ref2 (while loop with explicit addition)
 */
public class s5_java {
    public static int addNumbers(int[] nums) {
        int sum = 0;
        int i = 0;
        while (i < nums.length) {
            sum = sum + nums[i];
            i++;
        }
        return sum;
    }

    public static void main(String[] args) {
        int[] arr = { 10, 20, 30, 40, 50 };
        System.out.println("Total: " + addNumbers(arr));
    }
}
