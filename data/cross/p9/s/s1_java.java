/**
 * Student 1 — matches ref1 (iterative)
 */
public class s1_java {
    public static int peak(int[] a) {
        int m = a[0];
        for (int i = 1; i < a.length; i++) {
            if (a[i] > m)
                m = a[i];
        }
        return m;
    }

    public static void main(String[] args) {
        System.out.println(peak(new int[] { 1, 2 }));
    }
}
