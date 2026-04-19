// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int fibonacci(int n) {
        if ((n <= 1)) {
            return n;
        }
        int a;
        int b;
        a = 0;
        b = 1;
        for (int i = 2; (i <= n); i++) {
            int temp = (a + b);
            a = b;
            b = temp;
        }
        return b;
    }

    public static void main(String[] args) {
        System.out.println("Fib(7) = " + fibonacci(7));
    }
}
