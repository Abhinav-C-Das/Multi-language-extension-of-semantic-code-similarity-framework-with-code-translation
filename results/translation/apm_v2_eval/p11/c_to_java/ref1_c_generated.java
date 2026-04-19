// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static void bubbleSort(int[] arr) {
        for (int i = 0; (i < (arr.length - 1)); i++) {
            for (int j = 0; (j < ((arr.length - i) - 1)); j++) {
                if ((arr[j] > arr[(j + 1)])) {
                    int temp = arr[j];
                    arr[j] = arr[(j + 1)];
                    arr[(j + 1)] = temp;
                }
            }
        }
    }

    public static void main(String[] args) {
        int[] arr = new int[]{64, 34, 25, 12, 22, 11, 90};
        int n = 7;
        bubbleSort(arr);
        for (int i = 0; (i < n); i++) {
            System.out.print("" + arr[i] + " ");
        }
    }
}
