/**
 * Student 7 — matches ref1 (early exit)
 */
public class s7_java {
    public static int search(int[] v, int t) {
        for (int i = 0; i < v.length; i++) {
            if (v[i] == t)
                return i;
        }
        return -1;
    }

    public static void main(String[] a) {
        System.out.println(search(new int[] { 1, 2 }, 2));
    }
}
