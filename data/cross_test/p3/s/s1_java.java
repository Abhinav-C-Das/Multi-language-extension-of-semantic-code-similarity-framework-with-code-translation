public class s1_java {
    public static int findMax(int[] arr) {
        int maxVal = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > maxVal) {
                maxVal = arr[i];
            }
        }
        return maxVal;
    }

    public static void main(String[] args) {
        int[] data = { 3, 7, 2, 9, 5 };
        System.out.println("Max: " + findMax(data));
    }
}
