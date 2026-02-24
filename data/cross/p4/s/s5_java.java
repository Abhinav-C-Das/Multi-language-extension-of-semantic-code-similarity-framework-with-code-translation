/**
 * Student 5 — matches ref1 (sum += a[i]*b[i])
 */
public class s5_java {
    public static int compute(int[] a, int[] b) {
        int dot = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
        }
        return dot;
    }

    public static void main(String[] args) {
        int[] p = { 1, 3, 5 };
        int[] q = { 2, 4, 6 };
        System.out.println("Dot: " + compute(p, q));
    }
}
