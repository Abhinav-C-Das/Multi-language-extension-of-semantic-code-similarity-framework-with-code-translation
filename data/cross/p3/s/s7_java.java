/**
 * Student 7 — matches ref1 (product *= arr[i])
 */
public class s7_java {
    public static long prod(int[] values) {
        long out = 1;
        for (int i = 0; i < values.length; i++) {
            out *= values[i];
        }
        return out;
    }

    public static void main(String[] args) {
        int[] values = { 2, 3, 4, 5 };
        System.out.println("Prod: " + prod(values));
    }
}
