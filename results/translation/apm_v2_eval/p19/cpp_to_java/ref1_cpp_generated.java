// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static void selectionSort(int[] arr) {
        for (int i = 0; (i < (arr.length - 1)); i++) {
            int minIdx = i;
            for (int j = (i + 1); (j < arr.length); j++) {
                if ((arr[j] < arr[minIdx])) {
                    minIdx = j;
                }
            }
            int temp = arr[i];
            arr[i] = arr[minIdx];
            arr[minIdx] = temp;
        }
    }

    public static void main(String[] args) {
        int[] arr = new int[]{64, 25, 12, 22, 11};
        int n = 5;
        selectionSort(arr);
        for (int i = 0; (i < n); i++) {
            System.out.print("" + arr[i] + " ");
        }
        System.out.println();
    }
}
