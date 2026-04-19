// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = (arr.length - 1);
        while ((left <= right)) {
            int mid = (left + ((right - left) / 2));
            if ((arr[mid] == target)) {
                return mid;
            }
            if ((arr[mid] < target)) {
                left = (mid + 1);
            } else {
                right = (mid - 1);
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{2, 5, 8, 12, 16, 23, 38, 45, 56, 67, 78};
        int n = 11;
        int target = 23;
        int result = binarySearch(arr, target);
        System.out.println("Index: " + result);
    }
}
