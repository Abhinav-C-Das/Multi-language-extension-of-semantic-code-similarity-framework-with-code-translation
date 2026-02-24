/**
 * Reference 2: Balance Tracker — balance = balance - expenses[i]
 * CES: loop_ANY::ACCUMULATIVE::ASSIGN
 */
public class ref2_java {
    public static int trackBalance(int start, int[] expenses) {
        int balance = start;
        for (int i = 0; i < expenses.length; i++) {
            balance = balance - expenses[i];
        }
        return balance;
    }

    public static void main(String[] args) {
        int[] costs = { 50, 30, 20, 45, 15 };
        System.out.println("Remaining: " + trackBalance(500, costs));
    }
}
