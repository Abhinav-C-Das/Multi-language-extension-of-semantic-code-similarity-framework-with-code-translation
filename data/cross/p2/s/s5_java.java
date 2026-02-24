/**
 * Student 5 — matches ref2 (count = count + 1)
 */
public class s5_java {
    public static int numOccurrences(int[] list, int target) {
        int n = 0;
        for (int i = 0; i < list.length; i++) {
            if (list[i] == target) {
                n = n + 1;
            }
        }
        return n;
    }

    public static void main(String[] args) {
        int[] list = { 3, 7, 3, 2, 3, 8, 3, 1 };
        System.out.println("Occurrences: " + numOccurrences(list, 3));
    }
}
