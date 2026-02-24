/**
 * Student 7 — matches ref1 (balance -= expenses[i])
 */
public class s7_java {
    public static int netBalance(int initial, int[] debits) {
        int net = initial;
        for (int i = 0; i < debits.length; i++) {
            net -= debits[i];
        }
        return net;
    }

    public static void main(String[] args) {
        int[] d = { 50, 30, 20, 45, 15 };
        System.out.println("Net: " + netBalance(500, d));
    }
}
