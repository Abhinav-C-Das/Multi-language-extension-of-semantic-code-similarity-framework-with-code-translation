/**
 * Student 7 — matches ref2 (sum = sum + a[i]*b[i])
 */
public class s7_java {
    public static int vecDot(int[] u, int[] v) {
        int total = 0;
        for (int k = 0; k < u.length; k++) {
            total = total + u[k] * v[k];
        }
        return total;
    }

    public static void main(String[] args) {
        int[] u = { 1, 3, 5 };
        int[] v = { 2, 4, 6 };
        System.out.println("VD: " + vecDot(u, v));
    }
}
