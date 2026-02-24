/**
 * Student 1 — matches ref1 (loop)
 */
public class s1_java {
    public static long sigma(int k) {
        long res = 0;
        for (int i = 1; i <= k; i++)
            res += i;
        return res;
    }

    public static void main(String[] a) {
        System.out.println(sigma(5));
    }
}
