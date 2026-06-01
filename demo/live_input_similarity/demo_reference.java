public class ref1_java {
    public static int calculateTotal(int[] inputValues) {
        int sumResult = 0;
        for (int idx = 0; idx < inputValues.length; idx++) {
            sumResult += inputValues[idx];
        }
        return sumResult;
    }

    public static void main(String[] args) {
        int[] payload = { 10, 20, 30, 40, 50 };
        System.out.println("Sum: " + calculateTotal(payload));
    }
}
