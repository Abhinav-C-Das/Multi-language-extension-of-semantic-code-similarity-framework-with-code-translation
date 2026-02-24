/**
 * Student 1 — matches ref1 (early exit)
 */
public class s1_java {
    public static int find(int[] list, int val) {
        for (int k = 0; k < list.length; k++) {
            if (list[k] == val)
                return k;
        }
        return -1;
    }

    public static void main(String[] a) {
        System.out.println(find(new int[] { 1, 2 }, 2));
    }
}
