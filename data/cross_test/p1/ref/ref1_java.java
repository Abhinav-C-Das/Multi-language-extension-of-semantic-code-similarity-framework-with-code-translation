public class ref1_java {
    public static int sumArray(int[] arr) {
        int total = 0;
        for (int i = 0; i < arr.length; i++) {
            total += arr[i];
        }
        return total;
    }

    public static void main(String[] args) {
        int[] data = { 10, 20, 30, 40, 50 };
        System.out.println("Sum: " + sumArray(data));
    }
}
