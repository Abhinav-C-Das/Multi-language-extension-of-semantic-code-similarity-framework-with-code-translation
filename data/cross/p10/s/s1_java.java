/**
 * Student 1 — matches ref1 (bubble)
 */
public class s1_java {
    public static void sort(int[] a) {
        int N = a.length;
        for (int i = 0; i < N; i++) {
            for (int j = 1; j < (N - i); j++) {
                if (a[j - 1] > a[j]) {
                    int t = a[j - 1];
                    a[j - 1] = a[j];
                    a[j] = t;
                }
            }
        }
    }

    public static void main(String[] x) {
        sort(new int[] { 2, 1 });
    }
}
