// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int countOccurrences(int[] arr, int target) {
        int count = 0;
        for (int i = 0; (i < arr.length); i++) {
            if ((arr[i] == target)) {
                count++;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{5, 2, 5, 8, 5, 3};
        System.out.println("Count of 5: " + countOccurrences(arr, 5));
    }
}
