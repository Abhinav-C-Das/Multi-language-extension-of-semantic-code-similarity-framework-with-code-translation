public class MaxElement {
    public static int findMax(int[] arr) {
        if (arr.length == 0)
            return -1;
        int max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }

    public static void main(String[] args) {
        int[] numbers = { 45, 12, 89, 34, 67, 99, 23 };
        int maxNum = findMax(numbers);
        System.out.println("Maximum element is: " + maxNum);
    }
}
