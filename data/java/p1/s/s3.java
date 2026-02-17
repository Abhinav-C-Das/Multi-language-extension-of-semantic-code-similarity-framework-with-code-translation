/**
 * Student Submission 3
 * Should match: ref1 (indexed for loop with compound assignment)
 * Different variable names but same computational strategy
 */
public class s3 {
    public static int calculateSum(int[] data) {
        int sum = 0;
        for (int idx = 0; idx < data.length; idx++) {
            sum += data[idx];
        }
        return sum;
    }

    public static void main(String[] args) {
        int[] nums = { 10, 20, 30, 40, 50 };
        System.out.println("Sum is: " + calculateSum(nums));
    }
}
