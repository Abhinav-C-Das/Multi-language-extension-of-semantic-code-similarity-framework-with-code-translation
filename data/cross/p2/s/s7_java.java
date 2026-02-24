/**
 * Student 7 — matches ref1 (count += 1)
 */
public class s7_java {
    public static int countVal(int[] data, int val) {
        int sum = 0;
        for (int j = 0; j < data.length; j++) {
            if (data[j] == val) {
                sum += 1;
            }
        }
        return sum;
    }

    public static void main(String[] args) {
        int[] data = { 3, 7, 3, 2, 3, 8, 3, 1 };
        System.out.println("Total: " + countVal(data, 3));
    }
}
