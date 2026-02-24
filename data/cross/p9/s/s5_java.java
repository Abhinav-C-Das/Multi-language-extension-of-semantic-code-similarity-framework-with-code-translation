/**
 * Student 5 — matches ref2 (recursive)
 */
public class s5_java {
    public static int rfind(int[] a, int n) {
        if (n == 1)
            return a[0];
        int sub = rfind(a, n - 1);
        return Math.max(a[n - 1], sub);
    }

    public static void main(String[] args) {
        System.out.println(rfind(new int[] { 1, 2 }, 2));
    }
}
