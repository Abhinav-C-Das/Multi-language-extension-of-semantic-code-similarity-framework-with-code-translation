/**
 * Student 5 — matches ref2 (balance = balance - expenses[i])
 */
public class s5_java {
    public static int remaining(int funds, int[] costs) {
        int amount = funds;
        for (int i = 0; i < costs.length; i++) {
            amount = amount - costs[i];
        }
        return amount;
    }

    public static void main(String[] args) {
        int[] c = { 50, 30, 20, 45, 15 };
        System.out.println("Amount: " + remaining(500, c));
    }
}
