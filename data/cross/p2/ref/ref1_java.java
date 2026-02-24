/**
 * Reference Implementation 1: Count Occurrences
 * Strategy: Compound addition (+=)
 * CES Pattern: loop_ANY::ACCUMULATIVE::ADD
 */
public class ref1_java {
    public static int countOccurrences(int[] arr, int target) {
        int count = 0;
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                count += 1;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int[] data = { 3, 7, 3, 2, 3, 8, 3, 1 };
        System.out.println("Count: " + countOccurrences(data, 3));
    }
}
