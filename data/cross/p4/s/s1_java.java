/**
 * Student 1 — matches ref2 (sum = sum + a[i]*b[i])
 */
public class s1_java {
    public static int inner(int[] u, int[] v) {
        int result = 0;
        for (int i = 0; i < u.length; i++) {
            result = result + u[i] * v[i];
        }
        return result;
    }

    public static void main(String[] args) {
        int[] a = { 1, 3, 5 };
        int[] b = { 2, 4, 6 };
        System.out.println("Inner: " + inner(a, b));
    }
}
