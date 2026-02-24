/**
 * Student Submission 7
 * Should match: ref1 (indexed for loop with compound assignment)
 */
public class s7_java {
    public static int findTotal(int[] numbers) {
        int accumulator = 0;
        for (int index = 0; index < numbers.length; index++) {
            accumulator += numbers[index];
        }
        return accumulator;
    }

    public static void main(String[] args) {
        int[] input = {10, 20, 30, 40, 50};
        System.out.println("Sum = " + findTotal(input));
    }
}
