/**
 * Student 7 — matches ref1 (iterative)
 */
public class s7_java {
    public static int top(int[] data) {
        int t = data[0];
        for (int j = 1; j < data.length; j++) {
            if (data[j] > t)
                t = data[j];
        }
        return t;
    }

    public static void main(String[] args) {
        System.out.println(top(new int[] { 1, 2 }));
    }
}
