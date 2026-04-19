// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int linearSearchRecursive(int[] arr, int target, int index) {
        if ((index >= arr.length)) {
            return -1;
        }
        if ((arr[index] == target)) {
            return index;
        }
        return linearSearchRecursive(arr, target, (index + 1));
    }

    public static void main(String[] args) {
        int[] arr = new int[]{5, 10, 15, 20, 25};
        int n = 5;
        System.out.println("Found at: " + linearSearchRecursive(arr, 20, 0));
    }
}
